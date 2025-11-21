from docplex.mp.model import Model
import csv #엑셀명 : D_data.csv라 가정했을 때 버전입니다.

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
x = model.continuous_var_dict(all_indices, name='x',lb = 0)
#환자 수가 정수여서 함수를 integer_var_dict로 바꿔도 될 것 같습니다.
#lb : 비음수 조건 추가했습니다.
print(type(all_indices))

print(x)

# 딕셔너리 키(튜플)를 사용하여 해당 결정 변수 객체에 접근
# var_example = x[1, 2, 3, 1, 2]

print(type(x[1, 1, 1, 1, 2]))
a = [x[i,j,1,l,m]
    for i in I
    for j in J
    for l in L
    for m in M
    ]
#a라는 리스트에 k=1일 고정한 다른 모든 종류의 결정변수를 담겠다.

I_risk = {}
J_risk = {}
K_risk = {}
L_risk = {}
M_risk = {}

#의사 제약조건

#외과의사 제약조건
doctor_surgeon = [x[1,j,k,l,m]
                  for j in J
                  for k in K
                  for l in L
                  for m in M]
#1. 외과 (i = 1)
doctor_number_surgeon = 10        # 외과 의사 수 (예시)
doctor_work_time = 8              # 의사 근무시간 (예시)
visit_time_per_patient_surgeon = 0.5      # 외과 환자 1명당 진료시간(예시)

# 외과 환자 총 진료시간 = Σ(0.5 * x[1,j,k,l,m])
doctor_subject_surgeon = model.sum(
    visit_time_per_patient_surgeon * x[1, j, k, l, m]
    for j in J for k in K for l in L for m in M
)

# 제약식: 환자의 총 진료시간  <= 의사수 * 근무 시간
model.add_constraint(
    doctor_subject_surgeon <= doctor_number_surgeon * doctor_work_time,
    ctname="doctor_cap_surgery"# 제약식에 이름 붙이기
    #model.get_constraint_by_name("doctor_cap_surgery")

)


# 2. 내과 (i = 2)
doctor_internal = [x[2,j,k,l,m]
                  for j in J
                  for k in K
                  for l in L
                  for m in M]
doctor_number_internal = 12           # 내과 의사 수 (예시)
visit_time_per_patient_internal = 0.4 # 내과 환자 1명당 진료시간(예시)

doctor_subject_internal = model.sum(
    visit_time_per_patient_internal * x[2, j, k, l, m]
    for j in J for k in K for l in L for m in M
)

model.add_constraint(
    doctor_subject_internal <= doctor_number_internal * doctor_work_time,
    ctname="doctor_cap_internal"
)


# 3. 산부인과 (i = 3)

doctor_number_obgyn = 8               # 산부인과 의사 수 (예시)
visit_time_per_patient_obgyn = 0.6    # 산부인과 환자 1명당 진료시간(예시)

doctor_subject_obgyn = model.sum(
    visit_time_per_patient_obgyn * x[3, j, k, l, m]
    for j in J for k in K for l in L for m in M
)

model.add_constraint(
    doctor_subject_obgyn <= doctor_number_obgyn * doctor_work_time,
    ctname="doctor_cap_obgyn"
)


# 4. 소아청소년과 (i = 4)

doctor_number_pediatrics = 7              # 소아청소년과 의사 수 (예시)
visit_time_per_patient_pediatrics = 0.45  # 소아청소년과 환자 1명당 진료시간(예시)

doctor_subject_pediatrics = model.sum(
    visit_time_per_patient_pediatrics * x[4, j, k, l, m]
    for j in J for k in K for l in L for m in M
)

model.add_constraint(
    doctor_subject_pediatrics <= doctor_number_pediatrics * doctor_work_time,
    ctname="doctor_cap_pediatrics"
)

# 5. 이비인후과 (i = 5)

doctor_number_ent = 6                # 이비인후과 의사 수 (예시)
visit_time_per_patient_ent = 0.35    # 이비인후과 환자 1명당 진료시간(예시)

doctor_subject_ent = model.sum(
    visit_time_per_patient_ent * x[5, j, k, l, m]
    for j in J for k in K for l in L for m in M
)

model.add_constraint(
    doctor_subject_ent <= doctor_number_ent * doctor_work_time,
    ctname="doctor_cap_ent"
)

#병상제약코드
'''
중환자실 = 중환자만 배정 (j=1)
여자 일반 병실 - 일반환자 여성 (j=2, k=2)
남자 일반 병실 - 일반환자 남성 (j=2, k=1)
'''
# 병상 제약 설정
# 병상 수 (예시 숫자)
icu_beds = 20 #중환자실 침상 수
female_beds = 40 #여자 일반 병실 침상 수
male_beds = 45 #남자 일반 병실 침상 수

# 1. 중환자실 제약 (ICU)
icu_patients = model.sum(
    x[i, 1, k, l, m]
    for i in I
    for k in K
    for l in L
    for m in M
)
#중환자의 수 <= 중환자실 침상 수
model.add_constraint(
    icu_patients <= icu_beds,
    ctname="bed_cap_icu"
)

# 2. 여자 일반병실 제약
# 여성 일반 환자 수 ≤ 여자 일반병실 병상수

female_general_patients = model.sum(
    x[i, 2, 2, l, m]
    for i in I
    for l in L
    for m in M
)

model.add_constraint(
    female_general_patients <= female_beds,
    ctname="bed_cap_female_general"
)

# 3. 남자 일반병실 제약
# 남자 일반 환자 수 ≤ 남자 일반병실 병상수

male_general_patients = model.sum(
    x[i, 2, 1, l, m]
    for i in I
    for l in L
    for m in M
)

model.add_constraint(
    male_general_patients <= male_beds,
    ctname="bed_cap_male_general"
)


# 최대 환자 수 제약 (수요 상한: x <= D)
# D[i,j,k,l,m] : 내원 희망 환자 수
# -> CSV 파일에서 읽기 (D_data.csv, 헤더: i,j,k,l,m,D)

D = {idx: 0 for idx in all_indices}   #딕셔너리
'''
기본값 0으로 초기화
csv에 없는 조합이 있을 수도 있어서,
초기에 모든 조합의 D값을 0으로 채워넣는 코드입니다.
'''

with open("D_data.csv", newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)#csv헤더를 자동으로 key로 사용해서 dict로 반환
    for row in reader:
        i = int(row["i"])
        j = int(row["j"])
        k = int(row["k"])
        l = int(row["l"])
        m = int(row["m"])
        d_val = float(row["D"])
        key = (i, j, k, l, m) 
        if key in D:
            D[key] = d_val # D에 값 업데이트
        # csv에 있지만 all_indices에 없는 조합이면 무시

# x[i,j,k,l,m] <= D[i,j,k,l,m] 제약
max_patient_cts = model.add_constraints(
    (
        x[i, j, k, l, m] <= D[(i, j, k, l, m)],
        f"max_pat_{i}_{j}_{k}_{l}_{m}"
    )
    for (i, j, k, l, m) in all_indices
)
'''
조합별로 고유한 제약 이름을 자동으로 만들어주는 문자열
위반된 제약이 무엇인지 확인 가능
'''

# 7. 목적함수 설정 (예시)
#    → 전체 수용 환자 수 최대화

model.maximize(
    model.sum(x[i, j, k, l, m] for (i, j, k, l, m) in all_indices)
)

# 8. 모델 풀기

solution = model.solve(log_output=True)
#모델이 최대로 받아들인 환자 총합
if solution:
    print("Optimal objective value (총 수용 환자 수):", solution.objective_value)
else:
    print("해를 찾지 못했습니다.")

   