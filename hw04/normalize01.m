function normalized = normalize01(vector)
    min_val = min(vector);
    max_val = max(vector);
    normalized = (vector - min_val) / (max_val - min_val);
end
