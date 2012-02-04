% @2012 Christopher Brown (io@henrian.com), MIT licensed
function [label] = knnDistance(testImage, trainImages, trainLabels, K)

% knnsearch finds the nearest neighbor in X for each point in Y. X is an mx-by-n
%     matrix and Y is an my-by-n matrix. Rows of X and Y correspond to
%     observations and columns correspond to variables.
%size(eigenTrain) = [4000 4000]
%size(testImage) = [1 4000]
[IX, D] = knnsearch(trainImages, testImage, 'K', K);
if K > 1
%     topLabels = single(trainLabels(IX));
%     tab = tabulate(topLabels);
%     [~, IX2] = sort(tab(:,2), 'descend');
%     label = tab(IX2(1),1);
%     grpstats(trainLabels(IX))
    % find the potential labels
    kLabels = trainLabels(IX);
    actualK = length(kLabels);
    [b, ~, n] = unique(kLabels);
    multiplier = zeros(actualK, length(b));
    ones_at = sub2ind(size(multiplier), 1:actualK, n);
    multiplier(ones_at) = 1;
    average_distances = D*multiplier ./ sum(multiplier);
    [~, IX] = sort(average_distances);
    label = b(IX(1));
else
    label = trainLabels(IX);
end
