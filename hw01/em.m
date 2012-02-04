% @2012 Christopher Brown (io@henrian.com), MIT licensed
function [mu_diff, sigma_diff, percent_correct] = em(nclusters, ndims, nsamples, sd, draw_plots)
% e.g. [mu_diff sigma_diff correct] = em(2, 2, 500, 100, false);
mus = cell(1, nclusters);
sigmas = cell(nclusters);
% generate mu and sigma priors from some pretty simple standard normals
center = 0;
% sd = 1;
for c=1:nclusters,
  mus{c} = normrnd(center, sd, ndims, 1)';
  sigma_raw = normrnd(center, sd, ndims, ndims);
  sigmas{c} = sigma_raw * sigma_raw';
end

% generate gold_ps (the underlying model cluster priors) from a flat-ish dirichlet
gold_ps = gamrnd(ones(1, nclusters), 1);
gold_ps = gold_ps / sum(gold_ps);

% generate data from these priors
data = zeros(nsamples, ndims);
gold_labels = zeros(nsamples, 1);
for i=1:nsamples,
  [~, cluster_i] = max(gamrnd(gold_ps, 1));
  data(i,:) = mvnrnd(mus{cluster_i}, sigmas{cluster_i});
  gold_labels(i) = cluster_i;
end
% gold_ps should be very close to tabulate(gold_labels)(:,3) / 100

% xy_bounds = [min.x, max.x, min.y, max.y]
xy_bounds = [min(data(:,1)) max(data(:,1)) min(data(:,2)) max(data(:,2))];


% scatter and gold
if draw_plots
    clf; hold all;
    for c=1:nclusters, scatter(data(gold_labels == c,1), data(gold_labels == c,2)), end
    for c=1:nclusters, ezcontour(@(x,y) mvnpdf([x y], mus{c}, sigmas{c}), xy_bounds), end
end

% do built-in k-means clustering to get initial guess.
kmeans_labels = kmeans(data, nclusters);
% for each cluster, get all the points k-means thought were in that cluster,
%   and then predict mu and sigma parameters
post_mus = cell(1, nclusters);
post_sigmas = cell(nclusters);
for c=1:nclusters,
  cdata = data(kmeans_labels == c,:);
  post_mus{c} = mean(cdata);
  post_sigmas{c} = cov(cdata);
end
% random assignment
for c=1:nclusters,
  post_mus{c} = normrnd(center, sd, ndims, 1)';
  sigma_raw = normrnd(center, sd, ndims, ndims);
  post_sigmas{c} = sigma_raw * sigma_raw';
end

% scatter and guess
if draw_plots
    clf; hold all;
    for c=1:nclusters, scatter(data(gold_labels == c,1), data(gold_labels == c,2)), end
    for c=1:nclusters, ezcontour(@(x,y) mvnpdf([x y], post_mus{c}, post_sigmas{c}), xy_bounds), end
end

post_ps = ones(1, nclusters) / nclusters;

last_log_likelihood = -100;
fprintf('Iteration ...')
for x=1:100
    fprintf('%d ', x)
    % EXPECTATION (we guess posteriors)
    % ps is a matrix, where the columns are clusters, and rows correspond to data,
    %   and cells describe the log-likelihood that the data came from those clusters
    % j is the cluster index
    unweighted_posteriors = zeros(nsamples, nclusters);
    for j=1:nclusters
        unweighted_posteriors(:,j) = mvnpdf(data, post_mus{j}, post_sigmas{j}) * post_ps(j);
    end
    posteriors = bsxfun(@rdivide, unweighted_posteriors, sum(unweighted_posteriors, 2));


    % MAXIMIZATION (we set post_ps, post_mus, post_sigmas), j is the cluster index
    sum_posteriors = sum(posteriors);
    post_ps = sum_posteriors / nsamples;
    for j=1:nclusters,
        post_mus{j} = (posteriors(:,j)' * data) / sum_posteriors(j);

        post_sigma = zeros(ndims, ndims, nsamples);
        enough_mus = repmat(post_mus{j}, nsamples, 1);
        data_difference = data - enough_mus;
        for i=1:nsamples,
            post_sigma(:,:,i) = (data_difference(i,:)' * data_difference(i,:)) * posteriors(i,j);
        end
        post_sigmas{j} = sum(post_sigma,3) / sum_posteriors(j);
        
        [~, err] = cholcov(post_sigmas{j}, 0); % this is the error check that mvnpdf does
        if err ~= 0
            %fprintf('sigma error!\n');
            sigma_raw = normrnd(center, sd, ndims, ndims);
            post_sigmas{j} = sigma_raw * sigma_raw';
        end
    end
    
    % CONVERGENCE test
    log_likelihood = sum(log(sum(unweighted_posteriors)));
    % fprintf(' %.4f\n', log_likelihood);
    if (log_likelihood > last_log_likelihood && (log_likelihood - last_log_likelihood) < 0.0001)
        break;
    end
    last_log_likelihood = log_likelihood;
end

fprintf('\n');
% Gold P: %.5f ; Guess P: %.5f\n', gold_p, post_ps(1))

%labels_for_2dims = (posteriors(:,2) > posteriors(:,1)) + 1;
[~, labels] = max(posteriors, [], 2);

% deal with label switching (since labels are just categories)
map = @(array, mapper) arrayfun(@(x) mapper(x), array);
% I tried by size first, but it wasn't always nice.
% gold_tabulation = sortrows([(1:nclusters)' sortrows(tabulate(gold_labels), -2)], 2);
% sorted_gold_labels = map(gold_labels, gold_tabulation(:,1));
% post_tabulation = sortrows([(1:nclusters)' sortrows(tabulate(labels), -2)], 2);
% sorted_labels = map(labels,  post_tabulation(:,1));

% So I moved to brute force search of all pairings. this is about as 
% generous as is possible
remappings = perms(1:nclusters);
ne = zeros(1, length(remappings));
for remapping_i=1:length(remappings)
    remapped_labels = map(labels, remappings(remapping_i,:));
    ne(remapping_i) = sum(remapped_labels ~= gold_labels);
end
[~, remapping_i] = min(ne);
label_remapper = remappings(remapping_i,:);
fixed_labels = map(labels, label_remapper);

correctly_labeled = data(fixed_labels==gold_labels,:);
incorrectly_labeled = data(fixed_labels~=gold_labels,:);

if draw_plots
    clf; hold all;
    axis(xy_bounds);
    for c=1:nclusters, scatter(data(gold_labels == c,1), data(gold_labels == c,2), 20,'LineWidth',2), end
    for c=1:nclusters
        ezcontour(@(x,y) mvnpdf([x y], mus{c}, sigmas{c}), xy_bounds, 200);
    end
    % basically this maps the priors to the high range of the rainbow (blues,
    % purples), and the guessed parameters to the low range (red, orange)
    % awkward, since matlab doesn't let me set more than one color axis per
    % figure (at least, not easily/naturally)
    caxis([0 1]);
    for c=1:nclusters
        % matlab freaks out if I use 1.0 instead of 0.9999
        ezcontour(@(x,y) (0.9999 - mvnpdf([x y], post_mus{c}, post_sigmas{c})), xy_bounds, 200)
    end
    title('');
    scatter(correctly_labeled(:,1), correctly_labeled(:,2), 80, 'or','LineWidth',1.05);
    scatter(incorrectly_labeled(:,1), incorrectly_labeled(:,2), 80, 'xk','LineWidth',1.1);
end

mu_diffs = zeros(1, nclusters);
sigma_diffs = zeros(1, nclusters);
for c=1:nclusters
    mu_diffs(c) = sum(hypot(mus{c}, post_mus{label_remapper(c)}));
    sigma_diffs(c) = sum(hypot(sigmas{c}(:), post_sigmas{label_remapper(c)}(:)));
end

mu_diff = sum(mu_diffs);
sigma_diff = sum(sigma_diffs);
percent_correct = length(correctly_labeled) / nsamples;

%disp([sigmas{1}, [0; 0], post_sigmas{label_remapper(1)}])
%disp([sigmas{2}, [0; 0], post_sigmas{label_remapper(2)}])

