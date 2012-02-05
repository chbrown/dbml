% @2012 Christopher Brown (io@henrian.com), MIT licensed
% run these:
%   matlab -r crunch('easy5000-test.csv', 1:5000)
%   matlab -r crunch('hard5000-test.csv', 5000:10000)
%   matlab -r crunch('all10000-test.csv', 1:10000)
function crunch(csvPath, testIndices)

load hw2Data.mat;

nTest = length(testIndices);
[testImages, testLabels] = flatten4D(testImages, testLabels, testIndices);

todo = csvread(csvPath);
for line=1:size(todo, 1)
    if todo(line, 3) == -1
        nImages = todo(line, 1);
        [images, labels] = flatten4D(trainImages, trainLabels, 1:nImages);
        [m, fullV] = hw2FindEigendigits(images');
        topN = todo(line, 2);

        V = fullV(:,1:min(topN, size(fullV, 2)));

        eigenTrain = bsxfun(@minus, images, m') * V;
        eigenTest = bsxfun(@minus, testImages, m') * V;
        successes = zeros(1, nTest);
        for tt=1:nTest
            testImage = eigenTest(tt,:);
            [label] = knnDistance(testImage, eigenTrain, labels, 10);
            successes(tt) = (label == testLabels(tt));
        end
        result = sum(successes) / length(successes);

        fprintf('got results for nImages = %d, topN = %4d : %0.4f\n', nImages, topN, result);
        todo(line, 3) = result;
        csvwrite(csvPath, todo);
    end
end

% [p,q] = meshgrid(nImagesCandidates, topNCandidates);
% pairs = [p(:) q(:)];
