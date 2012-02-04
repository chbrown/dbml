% @2012 Christopher Brown (io@henrian.com), MIT licensed
function [label] = cosineDistance(testImage, trainImages, trainLabels)
nImages = size(trainImages, 2);
distances = ones(1, nImages);
for ii=1:nImages
    distances(ii) = pdist2(testImage, trainImages(ii,:), 'cosine');
end

[~, IX] = sort(distances);
label = trainLabels(IX(1));
