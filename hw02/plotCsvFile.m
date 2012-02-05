% @2012 Christopher Brown (io@henrian.com), MIT licensed
function plotCsvFile(csvFile, K)

% copied from eval
nImagesCandidates = [1 2 5 10 25 50 75 100 250 500 1000 5000 10000 30000 60000];
topNCandidates = [1 2 5 10 25 50 75 100 250 500 750 1000];

results = csvread(csvFile);
img = image(results, 'CDataMapping', 'scaled'); % 'scaled' is important!
set(gca, 'Color', 'none');
ylabel('Number of training Images');
set(gca,'YTick', 1:length(nImagesCandidates))
set(gca, 'YTickLabel', nImagesCandidates); % ii / nImages
xlabel('Top # of eigenvectors');
set(gca,'XTick', 1:length(topNCandidates))
set(gca, 'XTickLabel', topNCandidates); % jj / topNCandidates
title(sprintf('Results for kNN, where k = %d', K));

% export_fig plots/eigenvectors.pdf
