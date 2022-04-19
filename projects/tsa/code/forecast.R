# Data manipulation
library(readr)
library(dplyr)
library(lubridate)
# Time series analysis
library(tsibble)
library(fable)
library(feasts)

# Read in data
df <- read_csv('../data/tsa-backcast.csv')
df <- df |> mutate(Date = yearmonth(Date)) |>
    group_by(Date) |>
    summarise(Passengers = sum(Passengers)) |>
    as_tsibble(index = Date)

df <- df |> filter(Date < yearmonth(today()))
autoplot(df)

df_covid <- df |> filter(Date >= yearmonth("2020 Apr"))

fcst <- df |> model(
    ets = ETS(Passengers),
    arima = ARIMA(Passengers, stepwise = FALSE, approximation = FALSE),
    ets_log = ETS(log(Passengers)),
    arima_log = ARIMA(log(Passengers), stepwise = FALSE, approximation = FALSE)
    ) |>
    mutate(combo = (ets + arima) / 2) |>
    forecast(h = 9)

autoplot(fcst, df)
autoplot(fcst, df, level = NULL)
    

# Combine data and forecast
fcst <- fcst |>
    filter(.model == 'combo') |>
    as_tibble() |>
    select(Date, .mean) |>
    rename(Passengers = .mean)

df <- bind_rows(df, fcst)
autoplot(df)
write_csv(df, '../data/tsa-forecast.csv')

