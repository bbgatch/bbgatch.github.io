# Data manipulation and visualization
library(readr)
library(dplyr)
library(ggplot2)
# Time series analysis
library(tsibble)
library(fable)
library(feasts)

# Read in data
df <- read_csv('../data/tsa.csv')
df <- df |> as_tsibble(index = Date)

# Backcasting
fcst <- df |>
    # Remove Covid impact
    filter(Date <= '2020-02-29') |>
    # Create reverse index
    mutate(reverse_time = rev(row_number())) |>
    # Use new reverse index as tsibble index
    update_tsibble(index = reverse_time) |>
    # Create ETS and ARIMA models from data
    model(
        ets = ETS(Passengers),
        arima = ARIMA(Passengers, stepwise = FALSE, approximation = FALSE)
        ) |>
    # Create combined model from both
    mutate(combo = (ets + arima) / 2) |>
    forecast(h = 4) |>
    # Label newly forecasted data with proper historical dates
    mutate(Date = rep(df$Date[1] - c(1:4), 3)) |>
    # Reindex forecast results to use Date like the original data
    as_fable(index = Date, response = 'Passengers', distribution = 'Passengers')

# Plot backcasts with original data
autoplot(fcst, df |> filter(Date <= '2019-03-01')) +
    labs(title = 'Backcasts')

# Combine original data and forecast
fcst <- fcst |>
    filter(.model == 'combo') |>
    as_tibble() |>
    select(Date, .mean) |>
    rename(Passengers = .mean)
df <- bind_rows(df, fcst)

# Save data
write_csv(df, '../data/tsa-backcast.csv')

