source('~/.R.rc')
library(ggplot2)
library(scales)

setwd('/Volumes/Zooey/Dropbox/ut/machine-learning/hw07')

draw('results/qlearn.s50x10.o20.tsv', '50 x 10, 20 obstacles, e=0.9, g=0.8, a=0.01')
draw('results/qlearn.s50x10.o20.e99.tsv', '50 x 10, 20 obstacles, e=0.99, g=0.8, a=0.01')
draw('results/qlearn.s120x3.o10.tsv', '120 x 3, 10 obstacles, e=0.99, g=0.8, a=0.01')
draw('results/qlearn.s120x3.o10-2sight.tsv', '120 x 3, 10 obstacles, e=0.999, g=0.8, a=0.01, 2-away State Space')
draw('results/qlearn.s40x7.o10.e99-directions.tsv', '40 x 7, 10 obstacles, e=0.99, g=0.8, a=0.001, 2-away State Space')



# in.csv = 'results/qlearn-s40x7-o10-e9-directions-f.tsv'
# results = read.csv(in.csv)
# results = results[1:300,]

draw = function(in.csv, title) {
  results = read.csv(in.csv)

  p = ggplot(results, aes(x=epoch, y=reward/time, group=module)) + 
    geom_line(aes(colour=module), alpha=0.4) +
    geom_hline(aes(yintercept=0, colour='Obstacle Best')) +
    geom_hline(aes(yintercept=1, colour='Finish Best')) +
    geom_smooth(aes(colour=module)) +
    scale_colour_discrete(name="Modules") +
    ylab("Reward / time spent") + xlab("Time")
    
  options = opts(
      title=title,
      plot.title=theme_text(size=16, face="bold", vjust=1),
      axis.title.x=theme_text(face="bold", size=14),
      axis.title.y=theme_text(face="bold", size=14, angle=90, vjust=0.5, hjust=0.5),
      axis.text.x=theme_text(colour="black", size=12),
      axis.text.y=theme_text(colour="black", size=12),
      legend.text=theme_text(size=14),
      legend.title=theme_text(size=18, hjust=-0.01, face="bold")
    )

  print(p + options)
  out.nodots = sub('.', '-', in.csv)
  out.pdf = sub('-csv', '-pdf', out.nodots)
  ggsave(out.pdf, width=9, height=5)
}
draw('results/qlearn-s80x5-o10-e0.99-a0.001-g0.8-.csv', '80 x 5, 10 obstacles, e=0.99, g=0.8, a=0.001, High penalties')
draw('results/qlearn-s80x5-o10-e0.99-a0.001-g0.8-low.csv', '80 x 5, 10 obstacles, e=0.99, g=0.8, a=0.001, Low penalties')
draw('results/qlearn-s80x5-o6-high-penalty.csv', '80 x 5, 6 obstacles, e=0.9, g=0.8, a=0.01, High penalties')
