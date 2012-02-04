% @2012 Christopher Brown (io@henrian.com), MIT licensed

iterations = 50;
% col 1: mu      2: sigma       3: correct
results = zeros(iterations, 3);
for n=1:iterations
    % this doesn't work: results(n,:) = em(2, 2, 500, 100, false);
    [mu_diff sigma_diff correct] = em(2, 2, 500, 100, false);
    results(n,:) = [mu_diff sigma_diff correct];
end

% clf; hold all
% title('sd = 0.01')
% r = results1hundredth;
% plot(r(:,3))
% plot(r(:,1)/max(r(:,1)))
% plot(r(:,2)/max(r(:,2)))

