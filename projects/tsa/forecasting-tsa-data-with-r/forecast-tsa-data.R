# Standard packages
library(readr)
library(dplyr)
library(lubridate)
library(tidyr)
library(ggplot2)
library(scales)
library(forcats)
library(gt)

# Tidy time series packages
library(tsibble)
library(fable)
library(feasts)

# Read in and prepare data. Plot full history.
prepare_data <- function(){
    # Read in data
    df <- read_csv('../tsa.csv')
    tail(df)
    
    # Sum passengers by month
    df <- df |> 
        group_by(date = floor_date(date, "month")) |>
        summarise(passengers = sum(passengers)) |>
        # Exclude any extra dates in the current month where we don't have a 
        # full month of data
        filter(date < floor_date(today(), "month"))

    # Convert data to tsibble
    df <- df |> mutate(date = yearmonth(date))
    df <- df |> as_tsibble(index = date)

    # Plot data and return tsibble dataframe
    autoplot(df, passengers) + 
        ggtitle("TSA Passenger History") +
        scale_y_continuous(
            name="Passengers",
            labels=label_number(scale_cut = cut_short_scale())
        ) +
        theme(axis.title.x = element_blank())
    ggsave("images/tsa-passenger-history.png", width=16.18, height=10, units='cm')
    return(df)
}


# Time series decomposition
stl_decomposition <- function(df){
    dcmp <- df |>
        model(stl = STL(passengers))
    components(dcmp) |>
        autoplot() +
        scale_y_continuous(
            name="Passengers",
            labels=label_number(scale_cut = cut_short_scale())
        )
    ggsave("images/time-series-decomposition.png", width=16.18, height=10, units='cm')
}


# Compare models using train test split
train_test_models <- function(df){
    # The models will be more accurate if we ignore pre-Covid
    df <- df |> filter_index("2020-04" ~ .)

    # Split data into train/test sets
    size_of_data <- nrow(df)
    size_of_test <- round(size_of_data * 0.15)
    train <- df |> slice_head(n = size_of_data - size_of_test)
    test <- df |> slice_tail(n = size_of_test)
    months_to_forecast <- nrow(test)

    # Forecast with fable
    fit <- train |> model(
        # Baseline models
        mean = MEAN(passengers),
        naive = NAIVE(passengers),
        drift = NAIVE(passengers ~ drift()),
        snaive = SNAIVE(passengers),
        
        # Auto-ARIMA and Auto-ETS models
        arima = ARIMA(passengers, stepwise=FALSE, approximation=FALSE),
        # ets = ETS(passengers),

        tslm = TSLM(passengers ~ trend() + season()),
        
        # Additive error models
        # ets_ann = ETS(passengers ~ error('A') + trend('N') + season('N')),
        # ets_aan = ETS(passengers ~ error('A') + trend('A') + season('N')),
        # ets_aadn = ETS(passengers ~ error('A') + trend('Ad') + season('N')),
        # ets_ana = ETS(passengers ~ error('A') + trend('N') + season('A')),
        ets_aaa = ETS(passengers ~ error('A') + trend('A') + season('A')),
        ets_aada = ETS(passengers ~ error('A') + trend('Ad') + season('A')),

        ets_aam = ETS(passengers ~ error('A') + trend('A') + season('M')),
        ets_aadm = ETS(passengers ~ error('A') + trend('Ad') + season('M'))
    # Create combined models
    ) |> mutate(
        # arima_ets = (arima + ets) / 2,
        
        arima_ets_aaa = (arima + ets_aaa) / 2,
        arima_ets_aada = (arima + ets_aada) / 2,
        
        arima_ets_aam = (arima + ets_aam) / 2,
        arima_ets_aadm = (arima + ets_aadm) / 2
    )
    
    # Generate forecasts
    fcst <- fit |> forecast(h = months_to_forecast)
    
    # Save HTML table of model results
    accuracy(fcst, df) |>
        arrange(RMSE) # |>
        # gt() |>
        # as_raw_html() |>
        # writeLines("train-test-split-accuracy.html")
    
    # Plot results
    # autoplot(fcst, df, level = NULL)
    autoplot(filter(fcst, .model %in% c(
        'arima',
        'ets_aaa',
        'ets_aada',
        'arima_ets_aaa',
        'arima_ets_aada'
    )), df, level = NULL) +
        ggtitle("Top Forecast Models by RMSE on TSA Passenger Test Data") +
        scale_y_continuous(
            name="Passengers",
            labels=label_number(scale_cut = cut_short_scale())
        ) +
        theme(axis.title.x = element_blank())
    ggsave("images/train-test-top-forecast-models.png", width=16.18, height=10, units='cm')
}


# Compare models using cross validation
perform_cross_validation <- function(df){
    df_tr <- df |>
        filter_index("2020-04" ~ .) |>
        stretch_tsibble(.init=24, .step=1) |>
        # We want to test 12 months out, so the latest test set
        # can only have data through August 2023. This remove the 
        # last 12 monthly test sets.
        filter(!(.id %in% tail(unique(.id), 12)))
    
    fit <- df_tr |> model(
        # Baseline models
        mean = MEAN(passengers),
        naive = NAIVE(passengers),
        drift = NAIVE(passengers ~ drift()),
        snaive = SNAIVE(passengers),
        
        # Auto-ARIMA and Auto-ETS models
        arima = ARIMA(passengers, stepwise=FALSE, approximation=FALSE),
        # ets = ETS(passengers),

        tslm = TSLM(passengers ~ trend() + season()),
        
        # Additive error models
        # ets_ann = ETS(passengers ~ error('A') + trend('N') + season('N')),
        # ets_aan = ETS(passengers ~ error('A') + trend('A') + season('N')),
        # ets_aadn = ETS(passengers ~ error('A') + trend('Ad') + season('N')),
        # ets_ana = ETS(passengers ~ error('A') + trend('N') + season('A')),
        ets_aaa = ETS(passengers ~ error('A') + trend('A') + season('A')),
        ets_aada = ETS(passengers ~ error('A') + trend('Ad') + season('A')),
        
        # # ets_anm = ETS(passengers ~ error('A') + trend('N') + season('M')),
        # ets_aam = ETS(passengers ~ error('A') + trend('A') + season('M')),
        # ets_aadm = ETS(passengers ~ error('A') + trend('Ad') + season('M'))        
    
    ) |> mutate(
        arima_ets_aaa = (arima + ets_aaa) / 2,
        arima_ets_aada = (arima + ets_aada) / 2,
        # arima_ets_aam = (arima + ets_aam) / 2,
        # arima_ets_aadm = (arima + ets_aadm) / 2
        # # arima_ets = (arima + ets) / 2,
        # arima_ets_ann = (arima + ets_ann) / 2,
        # arima_ets_aan = (arima + ets_aan) / 2,
        # arima_ets_aadn = (arima + ets_aadn) / 2,
        # arima_ets_ana = (arima + ets_ana) / 2,
    )

    fcst <- fit |>
        forecast(h = 12)|>
        group_by(.id, .model) |>
        mutate(h = row_number()) |>
        ungroup() |>
        as_fable(response = "passengers", distribution = passengers)
    
    accuracy(fcst, df) |> arrange(RMSE)
    accuracy(filter(fcst, h == 12), df) |> arrange(RMSE)
    accuracy(fcst |> group_by(h), df) |> print(n=10000)
    
    # Plot forecast accuracy by months out
    accuracy(fcst |> group_by(h), df) |>
        filter(!(.model %in% c(
            'drift',
            'mean',
            'naive',
            'snaive',
            'tslm'
        ))) |>
        ggplot(mapping = aes(x = h, y = RMSE, color = .model)) +
        geom_line() +
        labs(
            title = "TSA Passenger History",
            x = "Forecast RMSE N Months Out"
        ) +
        scale_y_continuous(
            name="RMSE",
            labels=label_number(scale_cut = cut_short_scale())
        ) +
        scale_x_continuous(
            breaks = seq(1, 12)
            # breaks=breaks_pretty()
        ) +
        theme(panel.grid.minor = element_blank())
        
    ggsave("images/cross-validation-forecast-error.png", width=16.18, height=10, units='cm')

}


# Forecast data using chosen model
forecast_data <- function(df){
    # Forecast data using chosen models
    # The models will be more accurate if we ignore pre-Covid
    df <- df |> filter_index("2020-04" ~ .)

    # Find number of months to forecast
    months_to_forecast <- lubridate::interval(
        ym(max(df$date)) + months(1), ymd('2026-01-01')
    ) %/% months(1)
            
    # Forecast with fable
    fit <- df |> model(
        arima = ARIMA(passengers, stepwise=FALSE, approximation=FALSE),
        # ets = ETS(passengers),
        # ets_ann = ETS(passengers ~ error('A') + trend('N') + season('N')),
        # ets_aan = ETS(passengers ~ error('A') + trend('A') + season('N')),
        # ets_aadn = ETS(passengers ~ error('A') + trend('Ad') + season('N')),
        # ets_ana = ETS(passengers ~ error('A') + trend('N') + season('A')),
    
        # ets_aaa = ETS(passengers ~ error('A') + trend('A') + season('A')),
        ets_aada = ETS(passengers ~ error('A') + trend('Ad') + season('A')),
    
        # ets_aam = ETS(passengers ~ error('A') + trend('A') + season('M')),
        # ets_aadm = ETS(passengers ~ error('A') + trend('Ad') + season('M'))
    ) |> mutate(
    #   arima_ets_aaa = (arima + ets_aaa) / 2,
      arima_ets_aada = (arima + ets_aada) / 2
    )
    
    fcst <- fit |> forecast(h = months_to_forecast)
    # fcst <- fit |> forecast(h = 40)
    
    # Plot results
    autoplot(fcst, df)
    autoplot(fcst, df, level = NULL)
    autoplot(filter(fcst, .model %in% c('arima_ets_aada')), df)
    
    fcst <- fcst |> filter(.model == 'arima_ets_aada')
    
    return(fcst)
}


# Calculate annual percent change and plot monthly YoY percent change
plot_and_summarize_forecast <- function(df, fcst){
    fcst <- fcst |>
        as_tibble() |>
        select(date, .mean) |>
        rename(passengers = .mean)

    df <- bind_rows(df, fcst)

    # Calculate annual percent change in TSA Passengers
    results <- df |>
        as_tibble() |>
        mutate(Year = year(date)) |>
        group_by(Year) |>
        summarize(passengers = sum(passengers)) |>
        arrange(Year) |>
        mutate(pct_chg = percent((passengers / lag(passengers) - 1)))
    print(results)

    # Plot monthly year-over-year percent change trend
    monthly_chg <- df |>
        as_tibble() |>
        mutate(pct_chg = passengers / lag(passengers, 12) - 1)
    ggplot(monthly_chg, mapping = aes(x = date, y = pct_chg)) +
        geom_line()

}

# Run code
df <- prepare_data()
stl_decomposition(df)
train_test_models(df)
fcst <- forecast_data(df)
plot_and_summarize_forecast(df, fcst)
