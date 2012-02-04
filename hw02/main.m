% @2012 Christopher Brown (io@henrian.com), MIT licensed
% flatten = @(square) square(:);
% map = @(array, mapper) arrayfun(@(x) mapper(x), array);
% show = @(images, index) image(reshape(images(index,:), 28, 28));
% invert = @(images, index) image(255 - reshape(images(index,:), 28, 28));
% show(images, 1046);

% turnin to hychyc07
load hw2Data.mat;
%nImages = 2500; % = k
%fprintf('Training on %d samples.\n', nImages);
% size(trainImages) => 28          28           1       60000
% images: each row is one image, the columns are pixels
%[images, labels] = flatten4D(trainImages, trainLabels, 1:nImages);
% [m, V] = hw2FindEigendigits(images');


% power(2, 1:15)
nImagesCandidates = [1 2 5 10 25 50 75 100 250 500 1000 5000 10000 30000 50000];
topNCandidates = [1 2 5 10 25 50 75 100 250 500 750 1000];

% [testImages, testLabels] = flatten4D(trainImages, trainLabels, 50000:49999 + nTest);
nTest = 10000;
[testImages, testLabels] = flatten4D(testImages, testLabels, 1:nTest);
        
results = zeros(length(nImagesCandidates), length(topNCandidates));
for ii=1:length(nImagesCandidates)
    nImages = nImagesCandidates(ii);
    [images, labels] = flatten4D(trainImages, trainLabels, 1:nImages);
    [m, fullV] = hw2FindEigendigits(images');
    for jj=1:length(topNCandidates)
        topN = topNCandidates(jj);
        V = fullV(:,1:min(topN, size(fullV, 2)));

        eigenTrain = bsxfun(@minus, images, m') * V;
        eigenTest = bsxfun(@minus, testImages, m') * V;
        successes = zeros(1, nTest);
        for tt=1:nTest
            testImage = eigenTest(tt,:);
            goldLabel = testLabels(tt);
            [label] = knnDistance(testImage, eigenTrain, labels, 10);
            successes(tt) = label == goldLabel;
        end
        result = sum(successes) / length(successes);
        results(ii, jj) = result;
        fprintf('got results for nImages = %d, topN = %4d : %0.4f\n', nImages, topN, result);
    end
end

% imshow(results);
% colormap(gray);
% caxis
img = image(results, 'CDataMapping', 'scaled'); % 'scaled' is important!
set(gca, 'Color', 'none');
ylabel('Number of training Images');
set(gca,'YTick', 1:length(nImagesCandidates))
set(gca, 'YTickLabel', nImagesCandidates); % ii / nImages
xlabel('Top # of eigenvectors');
set(gca,'XTick', 1:length(topNCandidates))
set(gca, 'XTickLabel', topNCandidates); % jj / topNCandidates
title(sprintf('Results for kNN, where k = %d', 10));
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

eigenvectors = ones(28*10 + 9, 28*10 + 9);
for x=1:10
    for y=1:10
        insert_x = (x-1)*29+1;
        insert_y = (y-1)*29+1;
        eigenvectors(insert_y:insert_y + 27,insert_x:insert_x + 27) = reshape(fullV(:,x + 10*(y-1)), 28, 28);
    end
end
% imshow(eigenvectors*10);
