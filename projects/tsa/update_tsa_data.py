import code.pull_data as pull_data
import code.tidy_data as tidy_data
import code.plot_data as plot_data

# Set size of plot output images
width = 10
height = 6

# Pull updated TSA data and create plots
pull_data.pull_data()
tidy_data.tidy_data()
tidy_data.widen_data_by_year()
plot_data.plot_trend(width=width, height=height)
plot_data.plot_trend_by_year(width=width, height=height)
plot_data.plot_percent_change_trend(width=width, height=height)
plot_data.plot_percent_change_trend_by_year(width=width, height=height)
plot_data.plot_percent_of_2019_by_year(width=width, height=height)
