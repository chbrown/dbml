% @2012 Christopher Brown (io@henrian.com), MIT licensed
% This file is used to copy and paste ad-hoc commands into the Matlab command window,
% it is not intended to be run as a script

% flatten = @(square) square(:);
% map = @(array, mapper) arrayfun(@(x) mapper(x), array);
% show = @(images, index) image(reshape(images(index,:), 28, 28));
% invert = @(images, index) image(255 - reshape(images(index,:), 28, 28));
% show(images, 1046);

% turnin to hychyc07

% size(trainImages) => 28          28           1       60000
% images: each row is one image, the columns are pixels
% [images, labels] = flatten4D(trainImages, trainLabels, 1:nImages);
% [m, V] = hw2FindEigendigits(images');

% nTest = 10000;
% eval(nTest);

% imshow(results);
% colormap(gray);
% caxis

% colorbar('YTickLabel', 0:100);
% legend(img, 'First','Second','Third','Location','NorthEastOutside')
% export_fig knn10smart.pdf

% size(V) : [784 2500]
% topN = 500;
% fprintf('Using the first %d eigenvectors.\n', topN);

% csvwrite('cosineresults.csv', results)
% csvwrite('kn10-smart-results.csv', results)

% eval

% metricFn = @(testImage, trainImages, trainLabels) cosineDistance(testImage, trainImages, trainLabels);
% metricFn = @(testImage, trainImages, trainLabels) knnDistance(testImage, trainImages, trainLabels, 10);

    
    %fprintf('------------------------- (#%d) \n', tt);
    %fprintf('   goldLabel = %d\n', goldLabel);
    %fprintf('guessedLabel = %d\n', label);
    %disp([IX' topLabels']);

% fprintf('Tested %d images.\n', nTest);
% fprintf('Success rate: %0.4f\n', sum(successes) / length(successes));

plotCsvFile('metrics-1nn.csv', 1)
export_fig plots/metrics-1nn.pdf -transparent

plotCsvFile('metrics-10nn-vote.csv', 1)
title(sprintf('kNN, where k = %d (majority vote)', K));
export_fig plots/metrics-10nn-vote.pdf -transparent

plotCsvFile('metrics-10nn-weighted.csv', 1)
title(sprintf('kNN, where k = %d (weighted)', 10));
export_fig plots/metrics-10nn-weighted.pdf -transparent

plotCsvFile('metrics-cosine.csv', 1)
title(sprintf('Cosine similarity'));
export_fig plots/metrics-cosine.pdf -transparent

plotCsvFile('results-easy5000.csv', 0)
title('Easy 5000');
export_fig plots/results-easy-5000.pdf -transparent

plotCsvFile('results-hard5000.csv', 0)
title('Hard 5000');
export_fig plots/results-hard-5000.pdf -transparent

plotCsvFile('results-all10000.csv', 0)
title('All 10000');
export_fig plots/results-all-10000.pdf -transparent


rows = 10;
cols = 1;
indices = reshape(1:(rows * cols), cols, rows)';
eigenvectors = ones(28*rows + (rows - 1), 28*cols + (cols - 1));
for x=1:cols
    for y=1:rows
        insert_x = (x-1)*29+1;
        insert_y = (y-1)*29+1;
        image = reshape(fullV(:,indices(y, x)), 28, 28);
        eigenvectors(insert_y:insert_y + 27, insert_x:insert_x + 27) = image;
    end
end
imshow(eigenvectors*10);
export_fig plots/eigenvectors-25.pdf -transparent


% convert to-do csv to results matrix
todo = csvread('all10000-test.csv');
results = zeros(length(nImagesCandidates), length(topNCandidates));
for line=1:size(todo, 1)
    nImages = todo(line, 1);
    topN = todo(line, 2);
    result = todo(line, 3);
    
    nImagesCandidates = [1 2 5 10 25 50 75 100 250 500 1000 5000 10000 30000 60000];
    nImagesIndices = 1:length(nImagesCandidates);
    nImageIndex = nImagesIndices(nImagesCandidates==nImages);
    topNCandidates = [1 2 5 10 25 50 75 100 250 500 750 1000];
    topNIndices = 1:length(topNCandidates);
    topNIndex = nImagesIndices(topNCandidates==topN);
    
    results(nImageIndex, topNIndex) = result;
end
csvwrite('results-all10000.csv', results);


% digits(4);
% s = sym(A, 'd');
% v = vpa(results, 3);
% latex(s);
num2str(results, '%.3f & '); % output in latex-ish format
