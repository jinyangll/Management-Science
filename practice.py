from docplex.mp.model import Model

# 모델생성
model = Model(name='hospital_ip_model')

# 인덱스 i, j, k, l, m 집합 정의
I = range(1, 6) #진료 과목 4개정도로
J = range(1, 3) #중환자/일반환자
K = range(1, 3) #성별
L = range(1, 6) #나이대(유아, 청소년, 청년, 중년, 노년)
M = range(1, 4) #들어온 시간대 (day, eve, night)

# 모든 인덱스의 조합 (i, j, k, l, m)으로 구성된 튜플을 생성
all_indices = [(i, j, k, l, m) 
               for i in I 
               for j in J 
               for k in K 
               for l in L
               for m in M]

print(f"생성된 인덱스 튜플의 총 개수: {len(all_indices)}개")

# x는 딕셔너리 key : 각 인덱스(i, j, k, l, m) 튜플, value : 결정변수 객체
x = model.continuous_var_dict(all_indices, name='x')
print(type(all_indices))

print(x)

# 딕셔너리 키(튜플)를 사용하여 해당 결정 변수 객체에 접근
# var_example = x[1, 2, 3, 1, 2]

print(type(x[1, 1, 1, 1, 2]))
# <class 'docplex.mp.dvar.Var'>
#호출하는법
a = [x[i,j,1,l,m]
    for i in I
    for j in J
    for k in K
    for l in L
    for m in M
    ]
#a라는 리스트에 k=1일 고정한 다른 모든 종류의 결정변수를 담겠다.

I_risk = {}
J_risk = {}
K_risk = {}
L_risk = {}
M_risk = {}