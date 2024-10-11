# Forecasting TSA Passenger data with R ----------------------------------------

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
    df <- read_csv('tsa.csv')
    tail(df)
    
    # Sum passengers by month
    df <- df |> 
        group_by(date = floor_date(date, "month")) |>
        summarise(passengers = sum(passengers)) |>
        # Exclude any extra dates in the current month where we don't have a full month of data
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
        # tslm = TSLM(passengers ~ trend() + season()),
        
        # Auto-ARIMA and Auto-ETS models
        arima = ARIMA(passengers, stepwise=FALSE, approximation=FALSE),
        # ets = ETS(passengers),

        # ETS models
        ets_aaa = ETS(passengers ~ error('A') + trend('A') + season('A')),
        ets_aada = ETS(passengers ~ error('A') + trend('Ad') + season('A')),
        ets_aam = ETS(passengers ~ error('A') + trend('A') + season('M')),
        ets_aadm = ETS(passengers ~ error('A') + trend('Ad') + season('M'))
    )
    # Generate forecasts
    fcst <- fit |> forecast(h = months_to_forecast)
    
    # View model forecast accuracy against test set
    accuracy(fcst, df) |>
        arrange(RMSE) |>
        print()

    # Create combined models
    fcst <- fit |> mutate(
        arima_ets_aaa = (arima + ets_aaa) / 2,
        arima_ets_aada = (arima + ets_aada) / 2,
    ) |> forecast(h = months_to_forecast)
       
    # View model forecast accuracy against test set
    accuracy(fcst, df) |>
        arrange(RMSE) |>
        print()
    
    # Plot results
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


# Compare models using cross-validation
perform_cross_validation <- function(df){
    # Create cross-validation dataset
    df_tr <- df |>
        filter_index("2020-04" ~ .) |>
        # We need at least two years of data in order to fit the seasonal ETS models
        # This starts our base data with 24 months and increases each iteration by 1 month
        stretch_tsibble(.init=24, .step=1) |>
        # We want to forecast 12 months out in each iteration, so the last test set
        # can only have data through August 2023. This removes the last 12 monthly test sets.
        filter(!(.id %in% tail(unique(.id), 12)))
    
    # Fit models to CV dataset
    fit <- df_tr |> model(
        # Baseline models
        mean = MEAN(passengers),
        naive = NAIVE(passengers),
        drift = NAIVE(passengers ~ drift()),
        snaive = SNAIVE(passengers),
        # tslm = TSLM(passengers ~ trend() + season()),
        
        # Auto-ARIMA and Auto-ETS models
        arima = ARIMA(passengers, stepwise=FALSE, approximation=FALSE),
        # ets = ETS(passengers),

        ets_aaa = ETS(passengers ~ error('A') + trend('A') + season('A')),
        ets_aada = ETS(passengers ~ error('A') + trend('Ad') + season('A')),   
    
    # Add combined models
    ) |> mutate(
        arima_ets_aaa = (arima + ets_aaa) / 2,
        arima_ets_aada = (arima + ets_aada) / 2,
    )

    # Forecast 12 months ahead for each iteration
    fcst <- fit |>
        forecast(h = 12)|>
        group_by(.id, .model) |>
        mutate(h = row_number()) |>
        ungroup() |>
        # Need to convert back to a fable (forecast table) to use in the accuracy() function next
        as_fable(response = "passengers", distribution = passengers)
    
    # Print model accuracy
    accuracy(fcst, df) |> arrange(RMSE) |> print()
    
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
        ) +
        theme(panel.grid.minor = element_blank())
        
    ggsave("images/cross-validation-forecast-error.png", width=16.18, height=10, units='cm')

}


# Forecast data using chosen model
final_forecast <- function(df){
    # Forecast data using chosen models
    # The models will likely be more accurate if we ignore pre-Covid
    df_hist <- df
    df <- df |> filter_index("2020-04" ~ .)

    # Find number of months to forecast if we want a forecast through 2025
    months_to_forecast <- lubridate::interval(
        ym(max(df$date)) + months(1), ymd('2026-01-01')
    ) %/% months(1)
            
    # Fit models
    fit <- df |> model(
        arima = ARIMA(passengers, stepwise=FALSE, approximation=FALSE),
        ets_aada = ETS(passengers ~ error('A') + trend('Ad') + season('A')),
    ) |> mutate(
      arima_ets_aada = (arima + ets_aada) / 2
    )
    
    # Forecast
    fcst <- fit |> forecast(h = months_to_forecast)
    
    # Plot all three forecasts with prediction intervals
    autoplot(fcst, df) +
        ggtitle("TSA Passenger Forecast | ARIMA, ETS(A,Ad,A), and Combination") +
        scale_y_continuous(
            name="Passengers",
            labels=label_number(scale_cut = cut_short_scale())
        ) +
        theme(axis.title.x = element_blank())
    ggsave("images/final-forecast-three-models.png", width=16.18, height=10, units='cm')
       
    # Plot final combination model point forecast
    fcst <- fcst |> filter(.model == 'arima_ets_aada')
    autoplot(fcst, df_hist, level = NULL) +
        ggtitle("TSA Passenger Forecast | Combination ARIMA + ETS(A,Ad,A) Model") +
        scale_y_continuous(
            name="Passengers",
            labels=label_number(scale_cut = cut_short_scale())
        ) +
        theme(axis.title.x = element_blank())
    ggsave("images/final-forecast.png", width=16.18, height=10, units='cm')
       
    return(fcst)
}


# Calculate annual volume and percent change
calculate_annual_change <- function(df, fcst){
    fcst <- fcst |>
        as_tibble() |>
        select(date, .mean) |>
        rename(passengers = .mean)

    df <- bind_rows(df, fcst)

    # Calculate annual volume and percent change in TSA Passengers
    df |>
        as_tibble() |>
        mutate(Year = year(date)) |>
        group_by(Year) |>
        summarize(passengers = sum(passengers)) |>
        arrange(Year) |>
        mutate(pct_chg = percent((passengers / lag(passengers) - 1))) |>
        print()
}


# Run code
df <- prepare_data()
stl_decomposition(df)
train_test_models(df)
perform_cross_validation(df)
fcst <- final_forecast(df)
calculate_annual_change(df, fcst)