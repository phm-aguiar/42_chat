# Backlog: Cibersegurança

> Itens futuros para hardening do API Gateway (nginx) e da aplicação.
> Derivados da decisão de usar nginx como primeira barreira de segurança.

## Features Planejadas

### SEC-001: Rate Limiting + DDoS Mitigation
- Ativar `limit_req` e `limit_conn` já configurados no nginx.conf
- Rate limit por IP: 30 req/s com burst 20
- Conexões simultâneas: max 10 por IP
- Integrar com Redis para rate limiting distribuído (multi-instance)
- **Dependência:** nginx gateway (já deployado)

### SEC-002: HTTPS/TLS + Let's Encrypt
- Terminação TLS no nginx (certbot + Let's Encrypt)
- Redirect HTTP → HTTPS automático
- HSTS header com `max-age=31536000; includeSubDomains; preload`
- Renovação automática via cron
- **Dependência:** domínio público + SEC-001

### SEC-003: WAF Básico (nginx + ModSecurity)
- ModSecurity com OWASP Core Rule Set (CRS)
- Bloqueio de SQL injection, XSS, path traversal
- Log de violações para análise
- **Dependência:** nginx gateway

### SEC-004: Autenticação JWT no Gateway
- Validar JWT no nginx (nginx-jwt ou lua-resty-jwt)
- Rejeitar requests sem token ANTES de chegar no backend
- Cache de chave pública do JWT
- **Dependência:** nginx gateway + OpenResty

### SEC-005: IP Ban + Fail2ban
- Fail2ban lendo logs do nginx
- Ban automático após 5 falhas de auth em 60s
- Integração com iptables/nftables
- **Dependência:** nginx gateway

### SEC-006: Security Scanning Pipeline
- OWASP ZAP ou Nikto scan automatizado no CI
- Dependency scanning (npm audit, go mod tidy)
- Container scanning (Trivy ou Snyk)
- Relatório no PR
- **Dependência:** CI/CD (GitHub Actions)

### SEC-007: CSP + Security Headers Hardening
- Content-Security-Policy granular
- Subresource Integrity (SRI) nos assets
- Feature-Policy / Permissions-Policy completo
- Report-Only mode → enforce depois de tuning
- **Dependência:** build do frontend

## Ordem Sugerida
1. SEC-001 (rate limiting) — baixo esforço, já configurado
2. SEC-003 (WAF) — barreira de aplicação
3. SEC-004 (JWT no gateway) — validação precoce
4. SEC-002 (HTTPS) — requer domínio
5. SEC-005 (fail2ban) — complementa SEC-001
6. SEC-006 (scanning CI) — quality gate
7. SEC-007 (CSP) — hardening avançado

## Observações
- O nginx atual já tem `server_tokens off`, security headers básicos e zona de rate limiting definida (não ativada)
- A feature 009 (agent-pentester) do framework SDD pode ser integrada ao pipeline de segurança
- Backlog criado em 2026-06-17 durante setup do nginx gateway
