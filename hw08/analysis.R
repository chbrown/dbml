source('~/.R.rc')
library(ggplot2)
library(scales)
setwd('/Volumes/Zooey/Dropbox/ut/machine-learning/hw08')

draw = function(in.csv, plotfn, title) {
  tbl = read.csv(in.csv)
  p = plotfn(tbl) + 
    xlab("Iterations") +
    opts(
      title=title,
      plot.title=theme_text(size=16, face="bold", vjust=1),
      axis.title.x=theme_text(face="bold", size=14),
      axis.title.y=theme_text(face="bold", size=14, angle=90, vjust=0.5, hjust=0.5),
      axis.text.x=theme_text(colour="black", size=12),
      axis.text.y=theme_text(colour="black", size=12),
      legend.text=theme_text(size=14),
      legend.title=theme_text(size=18, hjust=-0.01, face="bold")
    )
  print(p)
  out.pdf = sub('.csv', '.pdf', in.csv)
  ggsave(out.pdf, width=9, height=5)
}

# iteration,best_fitness,best_length,worst_fitness,worst_length

fitnessfn = function(tbl) {
  ggplot(tbl, aes(x=iteration)) + 
    geom_line(aes(y=best_fitness, colour='Best')) +
    geom_line(aes(y=worst_fitness, colour='Worst')) +
    geom_hline(aes(yintercept=0, colour='Perfection')) +
    scale_colour_discrete(name="Runs") +
    ylab("Mistakes made") + xlab("Iterations")
}
draw('results/output-i600.csv', fitnessfn, 'Progressive best and worst solution fitness')

lengthfn = function(tbl) {
  ggplot(tbl, aes(x=iteration)) + 
    geom_line(aes(y=worst_length, colour='Worst'), alpha=0.7) +
    geom_line(aes(y=best_length, colour='Best')) +
    geom_hline(aes(yintercept=120, colour='Perfection')) +
    scale_colour_discrete(name="Runs") +
    ylab("Number of Swaps")
}
draw('results/output-i600.csv', lengthfn, 'Progressive best and worst solution length')

