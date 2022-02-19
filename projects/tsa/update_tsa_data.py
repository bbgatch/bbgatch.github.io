import code.pull_data as pull_data
import code.tidy_data as tidy_data
import code.plot_data as plot_data

pull_data.pull_data()
tidy_data.tidy_data()
tidy_data.widen_data_by_year()
plot_data.plot_trend()
plot_data.plot_trend_by_year()
plot_data.plot_percent_change_trend()
plot_data.plot_percent_change_trend_by_year()
plot_data.plot_percent_of_2019()
