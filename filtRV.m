function [R, V] = filtRV(Fs)
    
    Ts = 1 / Fs;

    freq_k = [660 1720 2410 3500 4500];
    sigma_k = [60 100 120 175 250];
    rho_k = zeros(5,1);

    for i = 1:5
        rho_k(i) = exp(-2 * pi * sigma_k(i) * Ts);
    end

    filters = [[1 -2*rho_k(1)*cos(2 * pi * freq_k(1) * Ts) rho_k(1)^2];
               [1 -2*rho_k(2)*cos(2 * pi * freq_k(2) * Ts) rho_k(2)^2];
               [1 -2*rho_k(3)*cos(2 * pi * freq_k(3) * Ts) rho_k(3)^2];
               [1 -2*rho_k(4)*cos(2 * pi * freq_k(4) * Ts) rho_k(4)^2];
               [1 -2*rho_k(5)*cos(2 * pi * freq_k(5) * Ts) rho_k(5)^2]];

    V = filters(1, 1:3);
    for i = 2:5
        c = conv(V, filters(i, 1:3));
        V = c;
    end

    R = [1 -0.96];
end