% @2012 Christopher Brown (io@henrian.com), MIT licensed
function [images, labels] = flatten4D(rawImages, rawLabels, indices)
nImages = length(indices);
images = zeros(nImages, size(rawImages, 1) * size(rawImages, 2));
for aa=1:nImages
    image = rawImages(:,:,1,indices(aa));
    images(aa,:) = double(image(:));
end
labels = rawLabels(indices);
