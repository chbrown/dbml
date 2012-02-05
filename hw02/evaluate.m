% @2012 Christopher Brown (io@henrian.com), MIT licensed
function evaluate(nTest, csvFile)

load hw2Data.mat;

nImagesCandidates = [1 2 5 10 25 50 75 100 250 500 1000 5000 10000 30000 50000];
topNCandidates = [1 2 5 10 25 50 75 100 250 500 750 1000];

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

csvwrite(csvFile, results)
