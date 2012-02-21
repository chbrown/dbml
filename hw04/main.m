% @2012 Christopher Brown (io@henrian.com), MIT licensed

%matlab -r "main(1:3, [2 5 1; 4 1 6; 7 2 3], 5000, 0.01)"
% length(indices) should equal ncols(A) -- nrows(A) is the number of
% listeners (mixed signals we record)
% function main(indices, A, R_max, eta)
indices = 1:5;
A = [5 1 2 1 3; 3 1 6 1 0; 2 7 3 1 4; 1 5 4 8 2; 4 0 1 4 7];
A = rand(2, 5);
eta = 0.01;
load sounds.mat; % [5 44000] = size(sounds)
U = sounds(indices,:); % [3 44000]
n = size(U, 1); % = length(indices)
X = A * U; % [m 44000]

Ys = cell(1, 10);
for i=1:10
    [W, Ws, Y] = ica(X, n, eta, 1000);

    remappings = perms(1:n);
    ne = zeros(1, length(remappings));
    for remapping_i=1:length(remappings)
        Y_remapped = Y(remappings(remapping_i,:),:);
        distances = zeros(1, length(n));
        for j=1:n
            distances(j) = pdist2(U(j,:), Y_remapped(j,:), 'cosine');
        end
        ne(remapping_i) = sum(distances);
    end
    [best_distance, best_remapping_i] = min(ne);
    Y_remapped = Y(remappings(best_remapping_i,:),:);

    Ys{i} = Y_remapped;
end

% clf;
% plot(Ws);
% title(sprintf('Flat W Parameters over learning iterations, for n = %d, m = %d, eta = %0.3f', n, m, eta));

T = size(U, 2);
clf;
hold on;
for i=1:n
    plot(normalize01(smooth(abs(U(i,:)'), 500, 'moving')) + 1.1*(i-1),'--g')
    for y=1:10
        Y = Ys{y};
        plot(normalize01(smooth(abs(Y(i,:)'), 500, 'moving')) + 1.1*(i-1),'r')
    end
    line([0 T], [1.1*(i-1) 1.1*(i-1)], 'Color', 'k')
end
xticks = get(gca, 'Xtick');
set(gca, 'xticklabel', sprintf('%d |', xticks'))
title('Inferred sources');
set(gca, 'YTickLabel', '');
legend('Original','Inferred','Location','NorthEast')
% title('Mixed sounds on three channels');
% title('Original (unmixed) sounds for first three channels');

% export_fig plots/5channels10-2mix.pdf -transparent

%soundsc(X', 11025); % play just the first two microphones (there may be more, but I have only two ears)
