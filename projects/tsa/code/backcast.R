# Data manipulation
library(readr)
library(dplyr)
# Time series analysis
library(tsibble)
library(fable)
library(feasts)

# Read in data
df <- read_csv('../data/tsa.csv')
df <- df |> as_tsibble(index = Date)

# Backcasting
fcst <- df |>
    filter(Date <= '2020-02-29') |>
    mutate(reverse_time = rev(row_number())) |>
    update_tsibble(index = reverse_time) |>
    model(
        ets = ETS(Passengers),
        arima = ARIMA(Passengers, stepwise = FALSE, approximation = FALSE)
        ) |>
    mutate(combo = (ets + arima) / 2) |>
    forecast(h = 4) |>
    mutate(Date = rep(df$Date[1] - (1:4), 3)) |>
    as_fable(index = Date, response = 'Passengers', distribution = 'Passengers')

autoplot(fcst, df |> filter(Date <= '2019-04-01')) +
    labs(title = 'Backcasts')

# Combine data and forecast
fcst <- fcst |>
    filter(.model == 'combo') |>
    as_tibble() |>
    select(Date, .mean) |>
    rename(Passengers = .mean)

df <- bind_rows(df, fcst)
write_csv(df, '../data/tsa-backcast.csv')

