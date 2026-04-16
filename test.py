n_kust = int(input())
kusts = list(map(int, input().split()))
best_sum = 0
sum = 0
for i in range(n_kust):
    sum = kusts[i-1] + kusts[i] + kusts[i+1 if i+1 != n_kust else 0]
    best_sum = max(sum, best_sum)
print(best_sum)