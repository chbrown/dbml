function [W, Ws, Y] = ica(X, n, eta, R_max)
    % X is the matrix of mixed signals
    % n is the number or original signals
    % eta is the learning rate
    % R_max is the number of interations
    m = size(X, 1);
    W = rand(n, m) / 100;
    Ws = zeros(R_max, length(W(:)));
    for i=1:R_max
        Y = W * X;
        Z = 1 ./ (1 + exp(-Y));
        inner = (1 - 2*Z) * Y';
        deltaW = eta .* ((eye(size(inner)) + inner) * W);
        W = W + deltaW;
        Ws(i,:) = W(:)';
    end
end

