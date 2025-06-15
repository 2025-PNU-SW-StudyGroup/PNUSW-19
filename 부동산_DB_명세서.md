### 📘 테이블: `UPIS_C_UQ111`
**설명:** 행정구역 사용용도 지리데이터(부동산 위치가 어떤 용도의 땅인지 분석하기 위함)

| 컬럼명 | 자료형 | 길이 | 기본값 | Nullable | PK 여부 | 설명 |
|--------|--------|------|---------|----------|---------|------|
| `id` | int4 | 32 | nextval('"UPIS_C_UQ111_id_seq"'::regclass) | NO | ✅ | 고유 식별자 |
| `geom` | geometry |  |  | YES |  | 공간 위치 정보 |
| `PRESENT_SN` | varchar | 24 |  | YES |  | 일련번호 |
| `LCLAS_CL` | varchar | 6 |  | YES |  | 대분류 코드 |
| `MLSFC_CL` | varchar | 6 |  | YES |  | 중분류 코드 |
| `SCLAS_CL` | varchar | 6 |  | YES |  | 소분류 코드 |
| `ATRB_SE` | varchar | 6 |  | YES |  | 속성 구분 코드 |
| `WTNNC_SN` | varchar | 20 |  | YES |  | 일련번호 |
| `NTFC_SN` | varchar | 20 |  | YES |  | 일련번호 |
| `DGM_NM` | varchar | 50 |  | YES |  | 도면 명칭 |
| `DGM_AR` | float8 | 53 |  | YES |  | 도면 면적 |
| `DGM_LT` | float8 | 53 |  | YES |  | 도면 길이 |
| `SIGNGU_SE` | varchar | 50 |  | YES |  | 시군구 명칭 |
| `DRAWING_NO` | varchar | 50 |  | YES |  | 도면 번호 |
| `CREATE_DAT` | date |  |  | YES |  | 생성 일자 |
| `SHAPE_AREA` | float8 | 53 |  | YES |  | 공간 면적 |
| `SHAPE_LEN` | float8 | 53 |  | YES |  | 공간 경계 길이 |

---

### 📘 테이블: `building_title_info`
**설명:** 건축물대장 API정보 (건물정보 분석용, DB안에는 데이터없음 외부에서 처리)

| 컬럼명 | 자료형 | 길이 | 기본값 | Nullable | PK 여부 | 설명 |
|--------|--------|------|---------|----------|---------|------|
| `mgm_bldrg_st_pk` | varchar | 30 |  | NO | ✅ | 관리 건축물대장 PK |
| `plat_plc` | varchar | 1000 |  | NO |  | 대지위치 |
| `sigungu_cd` | varchar | 30 |  | NO |  | 시군구코드 |
| `bjdong_cd` | varchar | 30 |  | NO |  | 법정동코드 |
| `plat_gb_cd` | varchar | 30 |  | YES |  | 대지구분코드(0:대지, 1:산, 2:블록) |
| `bun` | varchar | 20 |  | YES |  | 번 |
| `ji` | varchar | 20 |  | YES |  | 지 |
| `new_plat_plc` | varchar | 1000 |  | YES |  | 도로명대지위치 |
| `splot_nm` | varchar | 1000 |  | YES |  | 특수지명 |
| `block` | varchar | 500 |  | YES |  | 블록 |
| `lot` | varchar | 500 |  | YES |  | 로트 |
| `bylot_cnt` | int4 | 32 |  | YES |  | 외필지수 |
| `na_road_cd` | varchar | 30 |  | YES |  | 새주소도로코드 |
| `na_bjdong_cd` | varchar | 30 |  | YES |  | 새주소법정동코드 |
| `na_ugrnd_cd` | varchar | 30 |  | YES |  | 새주소지상지하코드 |
| `na_main_bun` | varchar | 20 |  | YES |  | 새주소본번 |
| `na_sub_bun` | varchar | 20 |  | YES |  | 새주소부번 |
| `bld_nm` | varchar | 200 |  | YES |  | 건물명 |
| `dong_nm` | varchar | 1000 |  | YES |  | 동명칭 |
| `main_atch_gb_cd` | varchar | 30 |  | YES |  | 주부속구분코드 |
| `main_atch_gb_cd_nm` | varchar | 1000 |  | YES |  | 주부속구분코드명 |
| `regstr_gb_cd` | varchar | 30 |  | YES |  | 대장구분코드 |
| `regstr_gb_cd_nm` | varchar | 1000 |  | YES |  | 대장구분코드명 |
| `regstr_kind_cd` | varchar | 30 |  | YES |  | 대장종류코드 |
| `regstr_kind_cd_nm` | varchar | 1000 |  | YES |  | 대장종류코드명 |
| `plat_area` | numeric | 30 |  | YES |  | 대지면적(㎡) |
| `arch_area` | numeric | 30 |  | YES |  | 건축면적(㎡) |
| `bc_rat` | numeric | 22 |  | YES |  | 건폐율(%) |
| `tot_area` | numeric | 30 |  | YES |  | 연면적(㎡) |
| `vl_rat_estm_tot_area` | numeric | 30 |  | YES |  | 용적률산정연면적(㎡) |
| `vl_rat` | numeric | 22 |  | YES |  | 용적률(%) |
| `tot_dong_tot_area` | numeric | 30 |  | YES |  | 총동연면적(㎡) |
| `strct_cd` | varchar | 2 |  | YES |  | 구조코드 |
| `strct_cd_nm` | varchar | 1000 |  | YES |  | 구조코드명 |
| `etc_strct` | varchar | 2000 |  | YES |  | 기타구조 |
| `main_purps_cd` | varchar | 5 |  | YES |  | 주용도코드 |
| `main_purps_cd_nm` | varchar | 1000 |  | YES |  | 주용도코드명 |
| `etc_purps` | varchar | 4000 |  | YES |  | 기타용도 |
| `roof_cd` | varchar | 30 |  | YES |  | 지붕코드 |
| `roof_cd_nm` | varchar | 1000 |  | YES |  | 지붕코드명 |
| `etc_roof` | varchar | 2000 |  | YES |  | 기타지붕 |
| `hhld_cnt` | int4 | 32 |  | YES |  | 세대수(세대) |
| `fmly_cnt` | int4 | 32 |  | YES |  | 가구수(가구) |
| `ho_cnt` | int4 | 32 |  | YES |  | 호수(호) |
| `heit` | numeric | 22 |  | YES |  | 높이(m) |
| `grnd_flr_cnt` | int4 | 32 |  | YES |  | 지상층수 |
| `ugrnd_flr_cnt` | int4 | 32 |  | YES |  | 지하층수 |
| `ride_use_elvt_cnt` | int4 | 32 |  | YES |  | 승용승강기수 |
| `emgen_use_elvt_cnt` | int4 | 32 |  | YES |  | 비상용승강기수 |
| `atch_bld_cnt` | int4 | 32 |  | YES |  | 부속건축물수 |
| `atch_bld_area` | numeric | 30 |  | YES |  | 부속건축물면적(㎡) |
| `indr_mech_utcnt` | int4 | 32 |  | YES |  | 옥내기계식대수(대) |
| `indr_mech_area` | numeric | 30 |  | YES |  | 옥내기계식면적(㎡) |
| `oudr_mech_utcnt` | int4 | 32 |  | YES |  | 옥외기계식대수(대) |
| `oudr_mech_area` | numeric | 30 |  | YES |  | 옥외기계식면적(㎡) |
| `indr_auto_utcnt` | int4 | 32 |  | YES |  | 옥내자주식대수(대) |
| `indr_auto_area` | numeric | 30 |  | YES |  | 옥내자주식면적(㎡) |
| `oudr_auto_utcnt` | int4 | 32 |  | YES |  | 옥외자주식대수(대) |
| `oudr_auto_area` | numeric | 30 |  | YES |  | 옥외자주식면적(㎡) |
| `pms_day` | varchar | 8 |  | YES |  | 허가일 |
| `stcns_day` | varchar | 8 |  | YES |  | 착공일 |
| `use_apr_day` | varchar | 8 |  | YES |  | 사용승인일 |
| `crtn_day` | varchar | 30 |  | NO |  | 생성일자 |
| `pmsno_year` | varchar | 4 |  | YES |  | 허가번호년 |
| `pmsno_kik_cd` | varchar | 30 |  | YES |  | 허가번호기관코드 |
| `pmsno_kik_cd_nm` | varchar | 1000 |  | YES |  | 허가번호기관코드명 |
| `pmsno_gb_cd` | varchar | 30 |  | YES |  | 허가번호구분코드 |
| `pmsno_gb_cd_nm` | varchar | 1000 |  | YES |  | 허가번호구분코드명 |
| `engr_grade` | varchar | 100 |  | YES |  | 에너지효율등급 |
| `engr_rat` | numeric | 22 |  | YES |  | 에너지절감율 |
| `engr_epi` | numeric | 22 |  | YES |  | EPI점수 |
| `gn_bld_grade` | varchar | 100 |  | YES |  | 친환경건축물등급 |
| `gn_bld_cert` | numeric | 22 |  | YES |  | 친환경건축물인증점수 |
| `itg_bld_grade` | varchar | 100 |  | YES |  | 지능형건축물등급 |
| `itg_bld_cert` | numeric | 22 |  | YES |  | 지능형건축물인증점수 |
| `rserthqk_dsgn_apply_yn` | varchar | 1 |  | YES |  | 내진설계적용여부(0,1) |
| `rserthqk_ablty` | varchar | 4000 |  | YES |  | 내진능력 |
| `rnum` | int4 | 32 |  | YES |  | 순번 |

---

### 📘 테이블: `bus_stop`
**설명:** 버스정류장 정보

| 컬럼명 | 자료형 | 길이 | 기본값 | Nullable | PK 여부 | 설명 |
|--------|--------|------|---------|----------|---------|------|
| `stop_id` | int4 | 32 |  | YES |  | 정류장 ID |
| `stop_name` | varchar | 50 |  | YES |  | 이름 |
| `stop_type` | varchar | 50 |  | YES |  | 정류장 유형 |
| `stop_number` | int4 | 32 |  | YES |  | 정류장 번호 |
| `latitude` | float4 | 24 |  | YES |  | 정보 없음 |
| `longitude` | float4 | 24 |  | YES |  | 정보 없음 |
| `bus_arrival_info_display_installed` | varchar | 50 |  | YES |  | 버스도착정보안내기_설치_여부 |
| `location` | geometry |  |  | YES |  | 정보 없음 |
| `id` | int8 | 64 | nextval('bus_stop_id_seq'::regclass) | NO | ✅ | 고유 식별자 |

---

### 📘 테이블: `cctv`
**설명:** CCTV정보

| 컬럼명 | 자료형 | 길이 | 기본값 | Nullable | PK 여부 | 설명 |
|--------|--------|------|---------|----------|---------|------|
| `region` | varchar | 50 |  | YES |  | 자치구 |
| `safe_address` | varchar | 200 |  | YES |  | 안심 주소 |
| `latitude` | float4 | 24 |  | YES |  | 정보 없음 |
| `longitude` | float4 | 24 |  | YES |  | 정보 없음 |
| `cctv_count` | int4 | 32 |  | YES |  | CCTV 수량 |
| `modified_datetime` | varchar | 50 |  | YES |  | 수정 일시 |
| `location` | geometry |  |  | YES |  | 정보 없음 |
| `id` | int8 | 64 | nextval('cctv_id_seq'::regclass) | NO | ✅ | 고유 식별자 |

---

### 📘 테이블: `favorite`
**설명:** 유저 선호데이터(사용안함)

| 컬럼명 | 자료형 | 길이 | 기본값 | Nullable | PK 여부 | 설명 |
|--------|--------|------|---------|----------|---------|------|
| `id` | int4 | 32 | nextval('favorite_id_seq'::regclass) | NO | ✅ | 고유 식별자 |
| `user_id` | int4 | 32 |  | NO |  | 정보 없음 |
| `property_id` | int4 | 32 |  | NO |  | 정보 없음 |
| `created_at` | timestamp |  | now() | YES |  | 정보 없음 |

---

### 📘 테이블: `property`
**설명:** 네이버 부동산 매물정보

| 컬럼명 | 자료형 | 길이 | 기본값 | Nullable | PK 여부 | 설명 |
|--------|--------|------|---------|----------|---------|------|
| `id` | int8 | 64 | nextval('property_id_seq'::regclass) | NO | ✅ | 고유 식별자 |
| `monthly_rent_cost` | int8 | 64 |  | NO |  | 정보 없음 |
| `deposit` | int8 | 64 |  | NO |  | 정보 없음 |
| `address` | varchar | 255 |  | YES |  | 주소 |
| `area` | numeric | 10 |  | NO |  | 정보 없음 |
| `floor` | int4 | 32 |  | YES |  | 정보 없음 |
| `property_type` | varchar | 50 |  | YES |  | 정보 없음 |
| `features` | varchar | 255 |  | YES |  | 정보 없음 |
| `direction` | varchar | 10 |  | YES |  | 정보 없음 |
| `residential_area` | varchar | 255 |  | YES |  | 정보 없음 |
| `location` | geometry |  |  | YES |  | 정보 없음 |
| `lot_number` | varchar | 100 |  | YES |  | 정보 없음 |
| `description` | text |  |  | YES |  | 정보 없음 |
| `agent_name` | varchar | 100 |  | NO |  | 이름 |
| `agent_office` | varchar | 100 |  | NO |  | 정보 없음 |
| `agent_phone` | varchar | 60 |  | NO |  | 정보 없음 |
| `agent_address` | text |  |  | NO |  | 주소 |
| `agent_registration_no` | text |  |  | NO |  | 정보 없음 |
| `created_at` | timestamp |  | now() | YES |  | 정보 없음 |
| `updated_at` | timestamp |  | now() | YES |  | 날짜 |
| `property_number` | varchar | 100 |  | YES |  | 정보 없음 |
| `administrative_code` | varchar | 20 |  | YES |  | 코드값 |
| `property_name` | varchar | 255 |  | YES |  | 이름 |
| `transaction_type` | varchar | 50 |  | YES |  | 정보 없음 |
| `confirmation_type` | varchar | 50 |  | YES |  | 정보 없음 |
| `supply_area` | numeric | 10 |  | YES |  | 정보 없음 |
| `property_confirmation_date` | date |  |  | YES |  | 날짜 |
| `main_image_url` | varchar | 255 |  | YES |  | 정보 없음 |
| `maintenance_cost` | int8 | 64 |  | YES |  | 정보 없음 |
| `rooms_bathrooms` | varchar | 50 |  | YES |  | 정보 없음 |
| `duplex` | bool |  | FALSE | YES |  | 정보 없음 |
| `available_move_in_date` | varchar | 100 |  | YES |  | 날짜 |
| `parking_spaces` | int4 | 32 |  | YES |  | 정보 없음 |
| `total_floor` | int4 | 32 |  | YES |  | 정보 없음 |
| `room_type` | varchar | 255 |  | YES |  | 정보 없음 |
| `elevator_count` | int4 | 32 |  | YES |  | 정보 없음 |
| `household_count` | int4 | 32 |  | YES |  | 정보 없음 |
| `family_count` | int4 | 32 |  | YES |  | 정보 없음 |
| `main_purpose` | varchar | 100 |  | YES |  | 정보 없음 |
| `etc_purpose` | varchar | 255 |  | YES |  | 정보 없음 |
| `structure_code` | varchar | 100 |  | YES |  | 코드값 |
| `approval_date` | date |  |  | YES |  | 날짜 |
| `is_checked` | bool |  | FALSE | YES |  | 정보 없음 |

---

### 📘 테이블: `property_bus_stop_map`
**설명:** 매물-1km이내 버스정류장 매핑테이블

| 컬럼명 | 자료형 | 길이 | 기본값 | Nullable | PK 여부 | 설명 |
|--------|--------|------|---------|----------|---------|------|
| `property_id` | int8 | 64 |  | NO | ✅ | 정보 없음 |
| `bus_stop_id` | int8 | 64 |  | NO | ✅ | 정류장 ID |
| `distance_meters` | float8 | 53 |  | NO |  | 정보 없음 |

---

### 📘 테이블: `property_cctv_map`
**설명:** 매물-1km이내 cctv 매핑테이블

| 컬럼명 | 자료형 | 길이 | 기본값 | Nullable | PK 여부 | 설명 |
|--------|--------|------|---------|----------|---------|------|
| `property_id` | int8 | 64 |  | NO | ✅ | 정보 없음 |
| `cctv_id` | int8 | 64 |  | NO | ✅ | 정보 없음 |
| `distance_meters` | float8 | 53 |  | NO |  | 정보 없음 |

---

### 📘 테이블: `property_photo`
**설명:** 매물 사진

| 컬럼명 | 자료형 | 길이 | 기본값 | Nullable | PK 여부 | 설명 |
|--------|--------|------|---------|----------|---------|------|
| `id` | int4 | 32 | nextval('property_photo_id_seq'::regclass) | NO | ✅ | 고유 식별자 |
| `property_id` | int4 | 32 |  | NO |  | 정보 없음 |
| `image_url` | text |  |  | NO |  | 정보 없음 |
| `image_type` | varchar | 50 |  | YES |  | 정보 없음 |
| `order` | int4 | 32 | 1 | YES |  | 정보 없음 |

---

### 📘 테이블: `property_rest_food_permit_map`
**설명:** 매물-1km이내 음식점매핑테이블

| 컬럼명 | 자료형 | 길이 | 기본값 | Nullable | PK 여부 | 설명 |
|--------|--------|------|---------|----------|---------|------|
| `property_id` | int8 | 64 |  | NO | ✅ | 정보 없음 |
| `rest_food_permit_id` | int8 | 64 |  | NO | ✅ | 정보 없음 |
| `distance_meters` | float8 | 53 |  | NO |  | 정보 없음 |

---

### 📘 테이블: `property_subway_map`
**설명:** 매물-1km이내 지하철매핑테이블

| 컬럼명 | 자료형 | 길이 | 기본값 | Nullable | PK 여부 | 설명 |
|--------|--------|------|---------|----------|---------|------|
| `property_id` | int8 | 64 |  | NO | ✅ | 정보 없음 |
| `subway_id` | int8 | 64 |  | NO | ✅ | 정보 없음 |
| `distance_meters` | float8 | 53 |  | NO |  | 정보 없음 |

---

### 📘 테이블: `property_tag`
**설명:** 매물 태그

| 컬럼명 | 자료형 | 길이 | 기본값 | Nullable | PK 여부 | 설명 |
|--------|--------|------|---------|----------|---------|------|
| `id` | int4 | 32 | nextval('property_tag_id_seq'::regclass) | NO | ✅ | 고유 식별자 |
| `property_id` | int4 | 32 |  | NO |  | 정보 없음 |
| `name` | text |  |  | NO |  | 이름 |

---

### 📘 테이블: `rest_food_permit`
**설명:** 음식점 정보

| 컬럼명 | 자료형 | 길이 | 기본값 | Nullable | PK 여부 | 설명 |
|--------|--------|------|---------|----------|---------|------|
| `opnsfteamcode` | varchar | 100 |  | YES |  | 코드값 |
| `mgtno` | varchar | 100 |  | YES |  | 정보 없음 |
| `apvpermyd` | varchar | 100 |  | YES |  | 정보 없음 |
| `apvcancelymd` | varchar | 100 |  | YES |  | 정보 없음 |
| `trdstategbn` | varchar | 100 |  | YES |  | 정보 없음 |
| `trdstatenm` | varchar | 100 |  | YES |  | 정보 없음 |
| `dtlstategbn` | varchar | 100 |  | YES |  | 정보 없음 |
| `dtlstatenm` | varchar | 100 |  | YES |  | 정보 없음 |
| `dcbymd` | varchar | 100 |  | YES |  | 정보 없음 |
| `clgstdt` | varchar | 100 |  | YES |  | 정보 없음 |
| `clgenddt` | varchar | 100 |  | YES |  | 정보 없음 |
| `ropnymd` | varchar | 100 |  | YES |  | 정보 없음 |
| `sitetel` | varchar | 100 |  | YES |  | 정보 없음 |
| `sitearea` | varchar | 100 |  | YES |  | 정보 없음 |
| `sitepostno` | varchar | 100 |  | YES |  | 정보 없음 |
| `sitewhladdr` | varchar | 300 |  | YES |  | 주소 |
| `rdnwhladdr` | varchar | 300 |  | YES |  | 주소 |
| `rdnpostno` | varchar | 100 |  | YES |  | 정보 없음 |
| `bplcnm` | varchar | 300 |  | YES |  | 정보 없음 |
| `lastmodts` | varchar | 100 |  | YES |  | 정보 없음 |
| `updategbn` | varchar | 100 |  | YES |  | 날짜 |
| `updatedt` | varchar | 100 |  | YES |  | 날짜 |
| `uptaenm` | varchar | 100 |  | YES |  | 정보 없음 |
| `x` | varchar | 100 |  | YES |  | 정보 없음 |
| `y` | varchar | 100 |  | YES |  | 정보 없음 |
| `sntuptaenm` | varchar | 100 |  | YES |  | 일련번호 |
| `maneipcnt` | varchar | 100 |  | YES |  | 정보 없음 |
| `wmeipcnt` | varchar | 100 |  | YES |  | 정보 없음 |
| `trdpjubnsenm` | varchar | 100 |  | YES |  | 정보 없음 |
| `lvsenm` | varchar | 100 |  | YES |  | 정보 없음 |
| `wtrspplyfacilsenm` | varchar | 100 |  | YES |  | 정보 없음 |
| `totepnum` | varchar | 100 |  | YES |  | 정보 없음 |
| `hoffeepcnt` | varchar | 100 |  | YES |  | 정보 없음 |
| `fctyowkepcnt` | varchar | 100 |  | YES |  | 정보 없음 |
| `fctysiljobepcnt` | varchar | 100 |  | YES |  | 정보 없음 |
| `fctypdtjobepcnt` | varchar | 100 |  | YES |  | 정보 없음 |
| `bdngownsenm` | varchar | 100 |  | YES |  | 정보 없음 |
| `isream` | varchar | 100 |  | YES |  | 정보 없음 |
| `monam` | varchar | 100 |  | YES |  | 정보 없음 |
| `multusnupsoyn` | varchar | 100 |  | YES |  | 일련번호 |
| `faciltotscp` | varchar | 100 |  | YES |  | 정보 없음 |
| `jtupsoasgnno` | varchar | 100 |  | YES |  | 정보 없음 |
| `jtupsomainedf` | varchar | 100 |  | YES |  | 정보 없음 |
| `homepage` | varchar | 300 |  | YES |  | 정보 없음 |
| `location` | geometry |  |  | YES |  | 정보 없음 |
| `id` | int8 | 64 | nextval('rest_food_permit_id_seq'::regclass) | NO | ✅ | 고유 식별자 |

---

### 📘 테이블: `spatial_ref_sys`
**설명:** 지리데이터 매핑정보

| 컬럼명 | 자료형 | 길이 | 기본값 | Nullable | PK 여부 | 설명 |
|--------|--------|------|---------|----------|---------|------|
| `srid` | int4 | 32 |  | NO |  | 정보 없음 |
| `auth_name` | varchar | 256 |  | YES |  | 이름 |
| `auth_srid` | int4 | 32 |  | YES |  | 정보 없음 |
| `srtext` | varchar | 2048 |  | YES |  | 정보 없음 |
| `proj4text` | varchar | 2048 |  | YES |  | 정보 없음 |

---

### 📘 테이블: `subway`
**설명:** 지하철 정보

| 컬럼명 | 자료형 | 길이 | 기본값 | Nullable | PK 여부 | 설명 |
|--------|--------|------|---------|----------|---------|------|
| `sequence_number` | varchar | 50 |  | YES |  | 연번 |
| `line_number` | varchar | 50 |  | YES |  | 호선 |
| `unique_station_code` | varchar | 50 |  | YES |  | 고유역번호(외부역코드) |
| `station_name` | varchar | 50 |  | YES |  | 역명 |
| `latitude` | varchar | 50 |  | YES |  | 정보 없음 |
| `longitude` | varchar | 50 |  | YES |  | 정보 없음 |
| `created_date` | varchar | 50 |  | YES |  | 작성일자 |
| `location` | geometry |  |  | YES |  | 정보 없음 |
| `id` | int8 | 64 | nextval('subway_id_seq'::regclass) | NO | ✅ | 고유 식별자 |

---

### 📘 테이블: `users`
**설명:** 유저정보(사용안함)

| 컬럼명 | 자료형 | 길이 | 기본값 | Nullable | PK 여부 | 설명 |
|--------|--------|------|---------|----------|---------|------|
| `id` | int4 | 32 | nextval('users_id_seq'::regclass) | NO | ✅ | 고유 식별자 |
| `email` | varchar | 255 |  | NO |  | 정보 없음 |
| `password` | varchar | 255 |  | NO |  | 정보 없음 |
| `created_at` | timestamp |  | now() | YES |  | 정보 없음 |

---
