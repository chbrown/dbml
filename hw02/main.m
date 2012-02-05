% @2012 Christopher Brown (io@henrian.com), MIT licensed
% flatten = @(square) square(:);
% map = @(array, mapper) arrayfun(@(x) mapper(x), array);
% show = @(images, index) image(reshape(images(index,:), 28, 28));
% invert = @(images, index) image(255 - reshape(images(index,:), 28, 28));
% show(images, 1046);

% turnin to hychyc07

% size(trainImages) => 28          28           1       60000
% images: each row is one image, the columns are pixels
%[images, labels] = flatten4D(trainImages, trainLabels, 1:nImages);
% [m, V] = hw2FindEigendigits(images');

% nTest = 10000;
% eval(nTest);

% [testImages, testLabels] = flatten4D(trainImages, trainLabels, 50000:49999 + nTest);

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

subV = fullV;
eigenvectors = ones(28*10 + 9, 28*10 + 9);
for x=1:10
    for y=1:10
        insert_x = (x-1)*29+1;
        insert_y = (y-1)*29+1;
        eigenvectors(insert_y:insert_y + 27,insert_x:insert_x + 27) = reshape(subV(:,x + 10*(y-1)), 28, 28);
    end
end
imshow(eigenvectors*10);
export_fig plots/eigenvectors.pdf
