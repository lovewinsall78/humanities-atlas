# 인문학 아틀라스 — 공개 사이트 배포 패키지

## 포함 파일
- `index.html`: 반응형 공개 사이트 (데모/실서비스 겸용)
- `schema.sql`: Supabase 회원·콘텐츠·학습기록 데이터베이스 및 RLS 보안 정책

## 바로 확인
`index.html`을 브라우저에서 열면 샘플 강연과 학습 UI를 볼 수 있습니다. 이 상태는 데모로, 공개 회원가입·관리자 등록은 비활성화되어 있습니다.

## 실제 공개 서비스 배포
1. Supabase 프로젝트를 만들고 SQL Editor에서 `schema.sql`을 실행합니다.
2. `index.html`의 `CONFIG.supabaseUrl`과 `CONFIG.supabaseAnonKey`를 프로젝트 URL과 공개 가능한 publishable/anon 키로 설정합니다. **service_role 키를 브라우저에 넣지 마세요.**
3. `index.html`을 Netlify 또는 Cloudflare Pages 정적 사이트로 배포합니다. HTTPS 도메인이 생성됩니다.
4. Supabase Authentication의 Site URL/Redirect URL에 실제 배포 주소를 등록하고 이메일 인증을 설정합니다.
5. 사이트에서 회원가입 후, Supabase SQL Editor에서 `update public.profiles set role='admin' where id=(select id from auth.users where email='관리자이메일');`을 실행합니다.
6. 관리자 계정으로 로그인하여 강연/명언을 등록하면 모든 방문자가 볼 수 있습니다.

## 운영 유의사항
- 현재 샘플 콘텐츠는 브라우저에서만 표시됩니다. Supabase 테이블이 비어 있다면 초기 샘플이 보이지만, 등록 이후에는 서버 콘텐츠가 우선 표시됩니다.
- 강연 자동 수집·자막 분석·AI 요약은 아직 구현되지 않았습니다. YouTube Data API 및 적법한 원고 확보, 서버 작업이 추가로 필요합니다.
- 일부 샘플 영상은 유튜브 ID가 없으므로 임베드되지 않습니다. 관리자 등록 화면에서 확인된 URL을 입력하세요.
- 샘플의 강연 소개·학습 질문은 원본 영상 전문을 검증한 요약이 아니라 교육용 편집 문구입니다.
- 공개 사이트에는 개인정보 처리방침, 이용약관, 운영자 정보, 신고·삭제 요청 경로, 콘텐츠 검수 정책을 추가해야 합니다.
- 이 서비스는 '이혜성의 1% 북클럽'의 공식 서비스가 아닙니다. 제휴 없이 공식 로고·브랜딩을 사용하거나 영상/자막을 무단 재게시하지 마세요. YouTube 임베드 및 링크 중심으로 운영하세요.
- 여러 기기 동기화는 Supabase 설정 및 로그인 후 작동합니다. 미로그인 기록은 브라우저 로컬 저장입니다.
