# 42 Intra API v2 — Documentacao Completa

**Fonte:** https://api.intra.42.fr/apidoc  
**Total de recursos:** 96  
**Total de endpoints:** 739  
**Auth:** OAuth 2.0 sobre HTTPS  
**Formato:** RESTful, JSON  

---

## Legenda
- 🔒 = Requer auth (restricted)
- 🌐 = Publico

---

## Accreditations Accreditations

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/accreditations` | 🌐 |
| GET | `/v2/accreditations/:id` | 🌐 |
| POST | `/v2/accreditations` | 🔒 |
| PATCH | `/v2/accreditations/:id` | 🔒 |
| PUT | `/v2/accreditations/:id` | 🔒 |
| DELETE | `/v2/accreditations/:id` | 🔒 |

## Achievements Meta-goals earned by users all along their progression.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/achievements` | 🔒 |
| GET | `/v2/cursus/:cursus_id/achievements` | 🔒 |
| GET | `/v2/campus/:campus_id/achievements` | 🔒 |
| GET | `/v2/titles/:title_id/achievements` | 🔒 |
| GET | `/v2/achievements/:id` | 🌐 |
| POST | `/v2/achievements` | 🔒 |
| PATCH | `/v2/achievements/:id` | 🔒 |
| PUT | `/v2/achievements/:id` | 🔒 |
| DELETE | `/v2/achievements/:id` | 🔒 |

## Achievements users Users which earned an achievement

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/achievements/:achievement_id/achievements_users` | 🌐 |
| GET | `/v2/achievements_users` | 🌐 |
| GET | `/v2/achievements_users/:id` | 🌐 |
| POST | `/v2/achievements_users` | 🔒 |
| PATCH | `/v2/achievements_users/:id` | 🔒 |
| PUT | `/v2/achievements_users/:id` | 🔒 |
| DELETE | `/v2/achievements_users/:id` | 🔒 |

## Alumnized users Alumnized users

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/alumnized_users` | 🔒 |

## Amendments Modifications applied to an internship.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/amendments` | 🌐 |
| GET | `/v2/users/:user_id/amendments` | 🌐 |
| GET | `/v2/internships/:internship_id/amendments` | 🌐 |
| GET | `/v2/amendments/:id` | 🌐 |
| POST | `/v2/amendments` | 🔒 |
| DELETE | `/v2/amendments/:id` | 🔒 |

## Announcements An announcement made to users in a cursus on their homepage.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/announcements/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/announcements/:id` | 🌐 |
| POST | `/v2/announcements` | 🔒 |
| POST | `/v2/cursus/:cursus_id/announcements` | 🔒 |
| PATCH | `/v2/announcements/:id` | 🔒 |
| PUT | `/v2/announcements/:id` | 🔒 |
| DELETE | `/v2/announcements/:id` | 🔒 |

## Anti grav units

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/anti_grav_units` | 🔒 |
| GET | `/v2/anti_grav_units/:id` | 🔒 |

## Anti grav units users

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/anti_grav_units_users` | 🔒 |
| GET | `/v2/users/:user_id/anti_grav_units_users` | 🔒 |
| GET | `/v2/campus/:campus_id/anti_grav_units_users` | 🔒 |
| GET | `/v2/anti_grav_units_users/:id` | 🔒 |
| POST | `/v2/anti_grav_units_users` | 🔒 |
| PATCH | `/v2/anti_grav_units_users/:id` | 🔒 |
| PUT | `/v2/anti_grav_units_users/:id` | 🔒 |

## Apps Applications for the API v2

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/apps` | 🌐 |
| GET | `/v2/users/:user_id/apps` | 🌐 |
| GET | `/v2/apps/:id` | 🌐 |

## Attachments All data which can be linked, like videos, pdfs, or links.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/project_sessions/:project_session_id/attachments` | 🌐 |
| GET | `/v2/projects/:project_id/attachments` | 🌐 |
| GET | `/v2/attachments` | 🌐 |
| GET | `/v2/project_sessions/:project_session_id/attachments/:id` | 🌐 |
| GET | `/v2/attachments/:id` | 🌐 |
| POST | `/v2/projects/:project_id/attachments` | 🔒 |
| PATCH | `/v2/attachments/:id` | 🔒 |
| PUT | `/v2/attachments/:id` | 🔒 |
| DELETE | `/v2/attachments/:id` | 🔒 |

## Balances The balance of a pool

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/balances` | 🔒 |
| GET | `/v2/pools/:pool_id/balances` | 🔒 |
| GET | `/v2/balances/:id` | 🔒 |
| GET | `/v2/pools/:pool_id/balances/:id` | 🔒 |
| PATCH | `/v2/balances/:id` | 🔒 |
| PUT | `/v2/balances/:id` | 🔒 |
| PATCH | `/v2/pools/:pool_id/balances/:id` | 🔒 |
| PUT | `/v2/pools/:pool_id/balances/:id` | 🔒 |

## Bloc deadlines A bloc

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/bloc_deadlines` | 🔒 |
| GET | `/v2/blocs/:bloc_id/bloc_deadlines` | 🔒 |
| GET | `/v2/bloc_deadlines/:id` | 🔒 |
| POST | `/v2/bloc_deadlines` | 🔒 |
| PATCH | `/v2/bloc_deadlines/:id` | 🔒 |
| PUT | `/v2/bloc_deadlines/:id` | 🔒 |

## Blocs A bloc is the managing container of coalitions.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/blocs` | 🌐 |
| GET | `/v2/blocs/:id` | 🌐 |

## Broadcasts Broadcasts publicated on a campus

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/campus/:campus_id/broadcasts` | 🌐 |

## Campus Places where 42 users works

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/campus` | 🌐 |
| GET | `/v2/campus/:id` | 🌐 |
| POST | `/v2/campus` | 🔒 |
| PATCH | `/v2/campus/:id` | 🔒 |
| PUT | `/v2/campus/:id` | 🔒 |
| GET | `/v2/campus/:campus_id/stats` | 🌐 |

## Campus users The users wich are in a campus

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/campus_users` | 🌐 |
| GET | `/v2/users/:user_id/campus_users` | 🌐 |
| GET | `/v2/campus_users/:id` | 🌐 |
| POST | `/v2/campus_users` | 🔒 |
| POST | `/v2/users/:user_id/campus_users` | 🔒 |
| POST | `/v2/campus_users/:id/set_as_primary` | 🔒 |

## Certificates certificates

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/certificates` | 🔒 |
| GET | `/v2/certificates/:id` | 🔒 |

## Certificates users User belonging to a certificate.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/certificates_users` | 🔒 |
| GET | `/v2/certificates/:certificate_id/certificates_users` | 🔒 |
| GET | `/v2/users/:user_id/certificates_users` | 🔒 |
| GET | `/v2/certificates_users/:id` | 🔒 |
| DELETE | `/v2/certificates_users/:id` | 🔒 |

## Closes The closing of a 42 account

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/closes` | 🔒 |
| GET | `/v2/users/:user_id/closes` | 🔒 |
| GET | `/v2/closes/:id` | 🔒 |
| POST | `/v2/closes` | 🔒 |
| POST | `/v2/users/:user_id/closes` | 🔒 |
| PATCH | `/v2/closes/:id` | 🔒 |
| PUT | `/v2/closes/:id` | 🔒 |
| DELETE | `/v2/closes/:id` | 🔒 |
| PATCH | `/v2/closes/:id/unclose` | 🔒 |
| PUT | `/v2/closes/:id/unclose` | 🔒 |
| PATCH | `/v2/closes/:id/close` | 🔒 |
| PUT | `/v2/closes/:id/close` | 🔒 |

## Clusters The clusters

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/clusters` | 🔒 |
| GET | `/v2/clusters/:id` | 🔒 |

## Coalitions A users competing inside of a bloc.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/coalitions` | 🌐 |
| GET | `/v2/users/:user_id/coalitions` | 🌐 |
| GET | `/v2/blocs/:bloc_id/coalitions` | 🌐 |
| GET | `/v2/coalitions/:id` | 🌐 |
| POST | `/v2/coalitions` | 🔒 |
| PATCH | `/v2/coalitions/:id` | 🔒 |
| PUT | `/v2/coalitions/:id` | 🔒 |

## Coalitions users coalition.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/coalitions/:coalition_id/coalitions_users` | 🌐 |
| GET | `/v2/coalitions_users` | 🌐 |
| GET | `/v2/users/:user_id/coalitions_users` | 🌐 |
| GET | `/v2/coalitions_users/:id` | 🌐 |
| POST | `/v2/coalitions_users` | 🔒 |
| PATCH | `/v2/coalitions_users/:id` | 🔒 |
| PUT | `/v2/coalitions_users/:id` | 🔒 |
| DELETE | `/v2/coalitions_users/:id` | 🔒 |

## Commands Products are sold on the intranet shop, here are commands

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/products/:product_id/commands` | 🌐 |
| GET | `/v2/campus/:campus_id/products/:product_id/commands` | 🌐 |

## Community services A task that an user have to do for the community. Usually linked with a close.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/community_services/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/closes/:close_id/community_services` | 🌐 |
| GET | `/v2/community_services` | 🌐 |
| GET | `/v2/community_services/:id` | 🌐 |
| PUT | `/v2/community_services/:id/validate` | 🔒 |
| PATCH | `/v2/community_services/:id/validate` | 🔒 |
| PUT | `/v2/community_services/:id/invalidate` | 🔒 |
| PATCH | `/v2/community_services/:id/invalidate` | 🔒 |
| POST | `/v2/community_services` | 🔒 |
| PATCH | `/v2/community_services/:id` | 🔒 |
| PUT | `/v2/community_services/:id` | 🔒 |
| DELETE | `/v2/community_services/:id` | 🔒 |

## Companies Companies from companies website

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/companies` | 🔒 |
| GET | `/v2/companies/:id` | 🔒 |
| GET | `/v2/companies/:company_id/subscribed_users` | 🔒 |
| GET | `/v2/companies/:company_id/internships_users` | 🔒 |

## Correction point historics

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/users/:user_id/correction_point_historics` | 🌐 |

## Cursus An educational cycle in 42

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/cursus` | 🌐 |
| GET | `/v2/cursus/:id` | 🌐 |
| POST | `/v2/cursus` | 🔒 |
| PATCH | `/v2/cursus/:id` | 🔒 |
| PUT | `/v2/cursus/:id` | 🔒 |
| DELETE | `/v2/cursus/:id` | 🔒 |

## Cursus users The users wich are in a cursus

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/cursus_users/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/cursus_users` | 🌐 |
| GET | `/v2/users/:user_id/cursus_users` | 🌐 |
| GET | `/v2/cursus/:cursus_id/cursus_users` | 🌐 |
| GET | `/v2/cursus_users/:id` | 🌐 |
| POST | `/v2/cursus_users` | 🔒 |
| POST | `/v2/users/:user_id/cursus_users` | 🔒 |
| PATCH | `/v2/cursus_users/:id` | 🔒 |
| PUT | `/v2/cursus_users/:id` | 🔒 |
| DELETE | `/v2/cursus_users/:id` | 🔒 |

## Dashes The Dash is a short-time project

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/dashes/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/dashes` | 🔒 |
| GET | `/v2/dashes/:id` | 🔒 |
| POST | `/v2/dashes` | 🔒 |
| PATCH | `/v2/dashes/:id` | 🔒 |
| PUT | `/v2/dashes/:id` | 🔒 |
| DELETE | `/v2/dashes/:id` | 🔒 |

## Dashes users The dash of a user

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/dashes_users/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/dashes_users` | 🌐 |
| GET | `/v2/dashes/:dash_id/dashes_users` | 🌐 |
| GET | `/v2/dashes_users/:id` | 🌐 |
| POST | `/v2/dashes_users` | 🔒 |
| PATCH | `/v2/dashes_users/:id` | 🔒 |
| PUT | `/v2/dashes_users/:id` | 🔒 |
| DELETE | `/v2/dashes_users/:id` | 🔒 |

## Endpoints A endpoint for a campus

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/endpoints` | 🔒 |
| GET | `/v2/endpoints/:id` | 🔒 |
| POST | `/v2/endpoints` | 🔒 |
| PATCH | `/v2/endpoints/:id` | 🔒 |
| PUT | `/v2/endpoints/:id` | 🔒 |
| DELETE | `/v2/endpoints/:id` | 🔒 |
| POST | `/v2/endpoints/:id/callback` | 🔒 |

## Evaluations The Evaluation of a project

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/evaluations` | 🔒 |
| GET | `/v2/evaluations/:id` | 🔒 |
| POST | `/v2/evaluations` | 🔒 |
| PATCH | `/v2/evaluations/:id` | 🔒 |
| PUT | `/v2/evaluations/:id` | 🔒 |
| DELETE | `/v2/evaluations/:id` | 🔒 |

## Events The events in a campus or a cursus

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/events/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/cursus/:cursus_id/events` | 🌐 |
| GET | `/v2/campus/:campus_id/events` | 🌐 |
| GET | `/v2/campus/:campus_id/cursus/:cursus_id/events` | 🌐 |
| GET | `/v2/users/:user_id/events` | 🌐 |
| GET | `/v2/events` | 🌐 |
| GET | `/v2/events/:id` | 🌐 |
| POST | `/v2/events` | 🔒 |
| PATCH | `/v2/events/:id` | 🔒 |
| PUT | `/v2/events/:id` | 🔒 |
| DELETE | `/v2/events/:id` | 🔒 |

## Events users Users registered to an event

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/users/:user_id/events_users` | 🌐 |
| GET | `/v2/events/:event_id/events_users` | 🌐 |
| GET | `/v2/events_users` | 🌐 |
| GET | `/v2/events_users/:id` | 🌐 |
| POST | `/v2/events_users` | 🔒 |
| PATCH | `/v2/events_users/:id` | 🔒 |
| PUT | `/v2/events_users/:id` | 🔒 |
| DELETE | `/v2/events_users/:id` | 🔒 |

## Exams The exam in a campus or a cursus

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/exams/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/cursus/:cursus_id/exams` | 🔒 |
| GET | `/v2/campus/:campus_id/exams` | 🔒 |
| GET | `/v2/campus/:campus_id/cursus/:cursus_id/exams` | 🔒 |
| GET | `/v2/users/:user_id/exams` | 🔒 |
| GET | `/v2/projects/:project_id/exams` | 🔒 |
| GET | `/v2/exams` | 🔒 |
| GET | `/v2/exams/:id` | 🌐 |
| POST | `/v2/exams` | 🔒 |
| PATCH | `/v2/exams/:id` | 🔒 |
| PUT | `/v2/exams/:id` | 🔒 |
| DELETE | `/v2/exams/:id` | 🔒 |

## Exams users

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/exams/:exam_id/exams_users` | 🔒 |
| POST | `/v2/exams/:exam_id/exams_users` | 🔒 |
| DELETE | `/v2/exams/:exam_id/exams_users/:id` | 🔒 |

## Experiences An experience gained by an user in a particular skill.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/experiences` | 🔒 |
| GET | `/v2/campus/:campus_id/experiences` | 🔒 |
| GET | `/v2/projects_users/:projects_user_id/experiences` | 🔒 |
| GET | `/v2/users/:user_id/experiences` | 🔒 |
| GET | `/v2/skills/:skill_id/experiences` | 🔒 |
| GET | `/v2/partnerships_users/:partnerships_user_id/experiences` | 🔒 |
| GET | `/v2/experiences/:id` | 🔒 |
| POST | `/v2/experiences` | 🔒 |
| PATCH | `/v2/experiences/:id` | 🔒 |
| PUT | `/v2/experiences/:id` | 🔒 |
| DELETE | `/v2/experiences/:id` | 🔒 |

## Expertises Pedagogic expertises

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/expertises` | 🌐 |
| GET | `/v2/expertises/:id` | 🌐 |
| POST | `/v2/expertises` | 🔒 |
| PATCH | `/v2/expertises/:id` | 🔒 |
| PUT | `/v2/expertises/:id` | 🔒 |
| DELETE | `/v2/expertises/:id` | 🔒 |

## Expertises users Users which have an expertise

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/expertises/:expertise_id/expertises_users` | 🌐 |
| GET | `/v2/users/:user_id/expertises_users` | 🌐 |
| GET | `/v2/expertises_users` | 🌐 |
| GET | `/v2/expertises_users/:id` | 🌐 |
| POST | `/v2/expertises/:expertise_id/expertises_users` | 🔒 |
| POST | `/v2/users/:user_id/expertises_users` | 🔒 |
| POST | `/v2/expertises_users` | 🔒 |
| PATCH | `/v2/expertises_users/:id` | 🔒 |
| PUT | `/v2/expertises_users/:id` | 🔒 |
| DELETE | `/v2/expertises_users/:id` | 🔒 |

## Feedbacks The feedback of a ScaleTeam or an Event

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/events/:event_id/feedbacks` | 🌐 |
| GET | `/v2/feedbacks` | 🌐 |
| GET | `/v2/scale_teams/:scale_team_id/feedbacks` | 🌐 |
| GET | `/v2/events/:event_id/feedbacks/:id` | 🌐 |
| GET | `/v2/feedbacks/:id` | 🌐 |
| GET | `/v2/scale_teams/:scale_team_id/feedbacks/:id` | 🌐 |
| POST | `/v2/events/:event_id/feedbacks` | 🔒 |
| POST | `/v2/feedbacks` | 🔒 |
| POST | `/v2/scale_teams/:scale_team_id/feedbacks` | 🔒 |
| PATCH | `/v2/events/:event_id/feedbacks/:id` | 🔒 |
| PUT | `/v2/events/:event_id/feedbacks/:id` | 🔒 |
| PATCH | `/v2/feedbacks/:id` | 🔒 |
| PUT | `/v2/feedbacks/:id` | 🔒 |
| PATCH | `/v2/scale_teams/:scale_team_id/feedbacks/:id` | 🔒 |
| PUT | `/v2/scale_teams/:scale_team_id/feedbacks/:id` | 🔒 |
| DELETE | `/v2/events/:event_id/feedbacks/:id` | 🔒 |
| DELETE | `/v2/feedbacks/:id` | 🔒 |
| DELETE | `/v2/scale_teams/:scale_team_id/feedbacks/:id` | 🔒 |

## Flags Flags from scales

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/flags` | 🌐 |

## Flash users The Flash Users

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/flashes/:flash_id/flash_users` | 🔒 |
| GET | `/v2/flash_users` | 🔒 |
| GET | `/v2/flashes/:flash_id/flash_users/:id` | 🔒 |
| GET | `/v2/flash_users/:id` | 🔒 |
| POST | `/v2/flashes/:flash_id/flash_users` | 🔒 |
| POST | `/v2/flash_users` | 🔒 |

## Flashes The Flash

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/flashes` | 🔒 |
| GET | `/v2/flashes/:id` | 🔒 |
| POST | `/v2/flashes` | 🔒 |

## Gitlab users

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/users/:user_id/gitlab_users` | 🔒 |

## Groups Groups in which users belong to. It will display a label on their profile and on the forum.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/groups` | 🌐 |
| GET | `/v2/users/:user_id/groups` | 🌐 |
| GET | `/v2/groups/:id` | 🌐 |
| POST | `/v2/groups` | 🔒 |
| PATCH | `/v2/groups/:id` | 🔒 |
| PUT | `/v2/groups/:id` | 🔒 |
| DELETE | `/v2/groups/:id` | 🔒 |

## Groups users Users who are in a group.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/groups_users` | 🌐 |
| GET | `/v2/groups/:group_id/groups_users` | 🌐 |
| GET | `/v2/users/:user_id/groups_users` | 🌐 |
| GET | `/v2/groups_users/:id` | 🌐 |
| POST | `/v2/groups_users` | 🔒 |
| PATCH | `/v2/groups_users/:id` | 🔒 |
| PUT | `/v2/groups_users/:id` | 🔒 |
| DELETE | `/v2/groups_users/:id` | 🔒 |

## Internships The internship

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/internships` | 🔒 |
| GET | `/v2/users/:user_id/internships` | 🔒 |
| POST | `/v2/internships` | 🔒 |
| PATCH | `/v2/internships/:id` | 🔒 |
| PUT | `/v2/internships/:id` | 🔒 |
| PATCH | `/v2/users/:user_id/internships/:id` | 🔒 |
| PUT | `/v2/users/:user_id/internships/:id` | 🔒 |
| GET | `/v2/internships/:id` | 🔒 |
| GET | `/v2/users/:user_id/internships/:id` | 🔒 |
| DELETE | `/v2/internships/:id` | 🔒 |

## Journals

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/campus/:campus_id/journals` | 🔒 |

## Languages The language

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/languages/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/languages` | 🌐 |
| GET | `/v2/languages/:id` | 🌐 |
| POST | `/v2/languages` | 🔒 |
| PATCH | `/v2/languages/:id` | 🔒 |
| PUT | `/v2/languages/:id` | 🔒 |
| DELETE | `/v2/languages/:id` | 🔒 |

## Languages users The languages of a user

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/languages_users/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/users/:user_id/languages_users` | 🌐 |
| GET | `/v2/languages_users` | 🌐 |
| GET | `/v2/users/:user_id/languages_users/:id` | 🌐 |
| GET | `/v2/languages_users/:id` | 🌐 |
| POST | `/v2/users/:user_id/languages_users` | 🔒 |
| POST | `/v2/languages_users` | 🔒 |
| PATCH | `/v2/users/:user_id/languages_users/:id` | 🔒 |
| PUT | `/v2/users/:user_id/languages_users/:id` | 🔒 |
| PATCH | `/v2/languages_users/:id` | 🔒 |
| PUT | `/v2/languages_users/:id` | 🔒 |
| DELETE | `/v2/users/:user_id/languages_users/:id` | 🔒 |
| DELETE | `/v2/languages_users/:id` | 🔒 |

## Levels A level indicator for a cursus.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/levels` | 🔒 |
| GET | `/v2/cursus/:cursus_id/levels` | 🔒 |

## Locations The location of an user in a campus

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/locations/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/locations` | 🌐 |
| GET | `/v2/users/:user_id/locations` | 🌐 |
| GET | `/v2/campus/:campus_id/locations` | 🌐 |
| GET | `/v2/locations/:id` | 🌐 |
| POST | `/v2/locations` | 🔒 |
| POST | `/v2/users/:user_id/locations` | 🔒 |
| PATCH | `/v2/locations/:id` | 🔒 |
| PUT | `/v2/locations/:id` | 🔒 |
| PATCH | `/v2/users/:user_id/locations/:id` | 🔒 |
| PUT | `/v2/users/:user_id/locations/:id` | 🔒 |
| DELETE | `/v2/locations/:id` | 🔒 |
| DELETE | `/v2/campus/:campus_id/locations/end_all` | 🔒 |

## Mailings Mails from and between 42 entities

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/mailings` | 🔒 |
| GET | `/v2/users/:user_id/mailings` | 🔒 |
| GET | `/v2/mailings/:id` | 🔒 |
| POST | `/v2/mailings` | 🔒 |
| PATCH | `/v2/mailings/:id` | 🔒 |
| PUT | `/v2/mailings/:id` | 🔒 |
| DELETE | `/v2/mailings/:id` | 🔒 |

## Notes A note for an user

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/users/:user_id/notes` | 🔒 |
| GET | `/v2/campus/:campus_id/notes` | 🔒 |
| GET | `/v2/notes` | 🔒 |
| GET | `/v2/notes/:id` | 🔒 |
| POST | `/v2/notes` | 🔒 |
| PATCH | `/v2/notes/:id` | 🔒 |
| PUT | `/v2/notes/:id` | 🔒 |
| DELETE | `/v2/notes/:id` | 🔒 |

## Notions The elearning notion in a cursus

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/cursus/:cursus_id/notions` | 🌐 |
| GET | `/v2/tags/:tag_id/notions` | 🌐 |
| GET | `/v2/notions` | 🌐 |
| GET | `/v2/notions/:id` | 🌐 |
| POST | `/v2/notions` | 🔒 |
| PATCH | `/v2/notions/:id` | 🔒 |
| PUT | `/v2/notions/:id` | 🔒 |
| DELETE | `/v2/notions/:id` | 🔒 |

## Offers Offers from companies website

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/offers` | 🌐 |
| GET | `/v2/offers/:id` | 🌐 |
| POST | `/v2/offers` | 🔒 |

## Offers users Users who have subscribed to an offer.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/offers/:offer_id/offers_users` | 🔒 |
| GET | `/v2/users/:user_id/offers_users` | 🔒 |
| GET | `/v2/offers_users` | 🔒 |
| GET | `/v2/offers_users/:id` | 🔒 |

## Params project sessions rules The value of a parameter for a project sessions rule.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/project_sessions_rules/:project_sessions_rule_id/params_project_sessions_rules` | 🔒 |
| GET | `/v2/params_project_sessions_rules` | 🔒 |
| GET | `/v2/params_project_sessions_rules/:id` | 🔒 |
| POST | `/v2/project_sessions_rules/:project_sessions_rule_id/params_project_sessions_rules` | 🔒 |
| POST | `/v2/params_project_sessions_rules` | 🔒 |
| PATCH | `/v2/params_project_sessions_rules/:id` | 🔒 |
| PUT | `/v2/params_project_sessions_rules/:id` | 🔒 |

## Partnerships Pedagogic partnerships

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/partnerships` | 🌐 |
| GET | `/v2/partnerships/:id` | 🌐 |
| POST | `/v2/partnerships` | 🔒 |
| PATCH | `/v2/partnerships/:id` | 🔒 |
| PUT | `/v2/partnerships/:id` | 🔒 |
| DELETE | `/v2/partnerships/:id` | 🔒 |

## Partnerships users Users doing a partnership

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/partnerships/:partnership_id/partnerships_users` | 🌐 |
| GET | `/v2/partnerships_users` | 🌐 |
| GET | `/v2/partnerships_users/:id` | 🌐 |
| POST | `/v2/partnerships/:partnership_id/partnerships_users` | 🔒 |
| POST | `/v2/partnerships_users` | 🔒 |
| PATCH | `/v2/partnerships_users/:id` | 🔒 |
| PUT | `/v2/partnerships_users/:id` | 🔒 |
| DELETE | `/v2/partnerships_users/:id` | 🔒 |

## Patronages A patronage between two users

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/patronages` | 🔒 |
| GET | `/v2/users/:user_id/patronages` | 🔒 |
| GET | `/v2/patronages/:id` | 🔒 |
| POST | `/v2/patronages` | 🔒 |
| POST | `/v2/users/:user_id/patronages` | 🔒 |
| PATCH | `/v2/patronages/:id` | 🔒 |
| PUT | `/v2/patronages/:id` | 🔒 |
| DELETE | `/v2/patronages/:id` | 🔒 |

## Patronages reports A report for a patronage

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/patronages_reports/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/patronages_reports` | 🔒 |
| GET | `/v2/users/:user_id/patronages_reports` | 🔒 |
| GET | `/v2/patronages/:patronage_id/patronages_reports` | 🔒 |
| GET | `/v2/reports/:report_id/patronages_reports` | 🔒 |
| GET | `/v2/patronages_reports/:id` | 🔒 |
| POST | `/v2/patronages_reports` | 🔒 |
| POST | `/v2/users/:user_id/patronages_reports` | 🔒 |
| POST | `/v2/patronages/:patronage_id/patronages_reports` | 🔒 |
| POST | `/v2/reports/:report_id/patronages_reports` | 🔒 |
| PATCH | `/v2/patronages_reports/:id` | 🔒 |
| PUT | `/v2/patronages_reports/:id` | 🔒 |
| DELETE | `/v2/patronages_reports/:id` | 🔒 |

## Pools The pool of evaluation points.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/pools` | 🔒 |
| GET | `/v2/pools/:id` | 🔒 |
| POST | `/v2/pools/:id/points/add` | 🔒 |
| DELETE | `/v2/pools/:id/points/remove` | 🔒 |

## Products Products are sold on the intranet shop

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/products` | 🌐 |
| GET | `/v2/campus/:campus_id/products` | 🌐 |
| GET | `/v2/products/:id` | 🌐 |
| GET | `/v2/campus/:campus_id/products/:id` | 🌐 |
| POST | `/v2/products` | 🔒 |
| POST | `/v2/campus/:campus_id/products` | 🔒 |
| PATCH | `/v2/products/:id` | 🔒 |
| PUT | `/v2/products/:id` | 🔒 |
| PATCH | `/v2/campus/:campus_id/products/:id` | 🔒 |
| PUT | `/v2/campus/:campus_id/products/:id` | 🔒 |
| DELETE | `/v2/products/:id` | 🔒 |
| DELETE | `/v2/campus/:campus_id/products/:id` | 🔒 |

## Project data Project data for the graph

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/project_data` | 🌐 |
| GET | `/v2/project_sessions/:project_session_id/project_data` | 🌐 |
| GET | `/v2/project_data/:id` | 🌐 |
| POST | `/v2/project_data` | 🔒 |
| PATCH | `/v2/project_data/:id` | 🔒 |
| PUT | `/v2/project_data/:id` | 🔒 |
| DELETE | `/v2/project_data/:id` | 🔒 |

## Project sessions A project session defines a particular behaviour for a project, based on the cursus and / or the campus .

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/projects/:project_id/project_sessions/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/project_sessions/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/projects/:project_id/project_sessions` | 🌐 |
| GET | `/v2/project_sessions` | 🌐 |
| GET | `/v2/project_sessions/:id` | 🌐 |

## Project sessions rules A rule linked to a project session.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/project_sessions/:project_session_id/project_sessions_rules` | 🔒 |
| GET | `/v2/project_sessions_rules` | 🔒 |
| GET | `/v2/project_sessions_rules/:id` | 🔒 |
| POST | `/v2/project_sessions/:project_session_id/project_sessions_rules` | 🔒 |
| POST | `/v2/project_sessions_rules` | 🔒 |
| PATCH | `/v2/project_sessions_rules/:id` | 🔒 |
| PUT | `/v2/project_sessions_rules/:id` | 🔒 |

## Project sessions skills A skill linked to a project session.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/project_sessions_skills` | 🌐 |
| GET | `/v2/project_sessions/:project_session_id/project_sessions_skills` | 🌐 |
| GET | `/v2/skills/:skill_id/project_sessions_skills` | 🌐 |
| GET | `/v2/project_sessions_skills/:id` | 🌐 |
| GET | `/v2/project_sessions/:project_session_id/project_sessions_skills/:id` | 🌐 |

## Projects Pedagogic projects of a cursus

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/cursus/:cursus_id/projects` | 🌐 |
| GET | `/v2/projects/:project_id/projects` | 🌐 |
| GET | `/v2/projects` | 🌐 |
| GET | `/v2/me/projects` | 🌐 |
| GET | `/v2/projects/:id` | 🌐 |
| POST | `/v2/projects` | 🔒 |
| PATCH | `/v2/projects/:id` | 🔒 |
| PUT | `/v2/projects/:id` | 🔒 |
| DELETE | `/v2/projects/:id` | 🔒 |
| PATCH | `/v2/projects/:id/retry` | 🔒 |
| PUT | `/v2/projects/:id/retry` | 🔒 |

## Projects users Users which did or are doing a project

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/projects/:project_id/projects_users/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/users/:user_id/projects_users/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/projects_users/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/projects/:project_id/projects_users` | 🌐 |
| GET | `/v2/users/:user_id/projects_users` | 🌐 |
| GET | `/v2/projects_users` | 🌐 |
| GET | `/v2/projects_users/:id` | 🌐 |
| POST | `/v2/projects/:project_id/projects_users` | 🔒 |
| POST | `/v2/users/:user_id/projects_users` | 🔒 |
| POST | `/v2/projects_users` | 🔒 |
| POST | `/v2/projects/:project_id/register` | 🔒 |
| PATCH | `/v2/projects_users/:id` | 🔒 |
| PUT | `/v2/projects_users/:id` | 🔒 |
| DELETE | `/v2/projects_users/:id` | 🔒 |
| PATCH | `/v2/projects_users/:id/compile` | 🔒 |
| PUT | `/v2/projects_users/:id/compile` | 🔒 |
| PATCH | `/v2/projects_users/:id/retry` | 🔒 |
| PUT | `/v2/projects_users/:id/retry` | 🔒 |
| POST | `/v2/projects_users/register_childs_and_scales` | 🔒 |
| DELETE | `/v2/projects_users/reset` | 🔒 |
| PATCH | `/v2/projects_users/scale` | 🔒 |

## Quests Quests which can or must be done by users

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/quests` | 🔒 |
| GET | `/v2/cursus/:cursus_id/quests` | 🔒 |
| GET | `/v2/campus/:campus_id/quests` | 🔒 |
| GET | `/v2/users/:user_id/quests` | 🔒 |
| GET | `/v2/quests/:id` | 🔒 |
| POST | `/v2/quests` | 🔒 |
| PATCH | `/v2/quests/:id` | 🔒 |
| PUT | `/v2/quests/:id` | 🔒 |
| DELETE | `/v2/quests/:id` | 🔒 |

## Quests users Users which earned an quest

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/quests_users/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/quests/:quest_id/quests_users` | 🌐 |
| GET | `/v2/users/:user_id/quests_users` | 🌐 |
| GET | `/v2/quests_users` | 🌐 |
| GET | `/v2/quests_users/:id` | 🌐 |
| POST | `/v2/quests_users` | 🔒 |
| PATCH | `/v2/quests_users/:id` | 🔒 |
| PUT | `/v2/quests_users/:id` | 🔒 |
| DELETE | `/v2/quests_users/:id` | 🔒 |

## Roles Grants particular privileges to entities like users and applications

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/roles` | 🌐 |
| GET | `/v2/users/:user_id/roles` | 🌐 |
| GET | `/v2/roles/:id` | 🌐 |
| POST | `/v2/roles` | 🔒 |
| PATCH | `/v2/roles/:id` | 🔒 |
| PUT | `/v2/roles/:id` | 🔒 |
| DELETE | `/v2/roles/:id` | 🔒 |

## Roles entities The applications linked to a role

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/roles_entities/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/roles/:role_id/roles_entities` | 🌐 |
| GET | `/v2/roles_entities` | 🌐 |
| GET | `/v2/roles_entities/:id` | 🌐 |
| POST | `/v2/roles_entities` | 🔒 |
| PATCH | `/v2/roles_entities/:id` | 🔒 |
| PUT | `/v2/roles_entities/:id` | 🔒 |
| DELETE | `/v2/roles_entities/:id` | 🔒 |

## Rules A rule for a project

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/rules` | 🔒 |
| GET | `/v2/project_sessions/:project_session_id/rules` | 🔒 |
| GET | `/v2/rules/:id` | 🔒 |
| POST | `/v2/rules` | 🔒 |
| POST | `/v2/project_sessions/:project_session_id/rules` | 🔒 |
| PATCH | `/v2/rules/:id` | 🔒 |
| PUT | `/v2/rules/:id` | 🔒 |
| DELETE | `/v2/rules/:id` | 🔒 |

## Scale teams A defence of a team (on a project), involving an evaluator

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/scale_teams/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/projects/:project_id/scale_teams/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/users/:user_id/scale_teams/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/project_sessions/:project_session_id/scale_teams` | 🌐 |
| GET | `/v2/scale_teams` | 🌐 |
| GET | `/v2/projects/:project_id/scale_teams` | 🌐 |
| GET | `/v2/users/:user_id/scale_teams/as_corrector` | 🌐 |
| GET | `/v2/users/:user_id/scale_teams/as_corrected` | 🌐 |
| GET | `/v2/users/:user_id/scale_teams` | 🌐 |
| GET | `/v2/me/scale_teams/as_corrector` | 🌐 |
| GET | `/v2/me/scale_teams/as_corrected` | 🌐 |
| GET | `/v2/me/scale_teams` | 🌐 |
| GET | `/v2/project_sessions/:project_session_id/scale_teams/:id` | 🌐 |
| GET | `/v2/scale_teams/:id` | 🌐 |
| POST | `/v2/project_sessions/:project_session_id/scale_teams` | 🔒 |
| POST | `/v2/scale_teams` | 🔒 |
| PATCH | `/v2/project_sessions/:project_session_id/scale_teams/:id` | 🔒 |
| PUT | `/v2/project_sessions/:project_session_id/scale_teams/:id` | 🔒 |
| PATCH | `/v2/scale_teams/:id` | 🔒 |
| PUT | `/v2/scale_teams/:id` | 🔒 |
| DELETE | `/v2/project_sessions/:project_session_id/scale_teams/:id` | 🔒 |
| DELETE | `/v2/scale_teams/:id` | 🔒 |
| POST | `/v2/scale_teams/multiple_create` | 🔒 |

## Scales A scale is composed by questions which allows an users to rate the quality of a project .

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/project_sessions/:project_session_id/scales` | 🔒 |
| GET | `/v2/scales` | 🔒 |
| GET | `/v2/projects/:project_id/scales` | 🔒 |
| GET | `/v2/users/:user_id/scales` | 🔒 |
| GET | `/v2/scales/:id` | 🔒 |
| POST | `/v2/scales` | 🔒 |
| PATCH | `/v2/scales/:id` | 🔒 |
| PUT | `/v2/scales/:id` | 🔒 |
| DELETE | `/v2/scales/:id` | 🔒 |

## Scores Points given to a coalition.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/scores` | 🔒 |
| GET | `/v2/coalitions/:coalition_id/scores` | 🔒 |
| GET | `/v2/coalitions_users/:coalitions_user_id/scores` | 🔒 |
| GET | `/v2/blocs/:bloc_id/scores` | 🔒 |
| GET | `/v2/scores/:id` | 🔒 |
| GET | `/v2/coalitions/:coalition_id/scores/:id` | 🔒 |
| GET | `/v2/coalitions_users/:coalitions_user_id/scores/:id` | 🔒 |
| GET | `/v2/blocs/:bloc_id/scores/:id` | 🔒 |
| POST | `/v2/coalitions/:coalition_id/scores` | 🔒 |
| DELETE | `/v2/coalitions/:coalition_id/scores/:id` | 🔒 |

## Skills A particlar skill.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/skills` | 🌐 |
| GET | `/v2/cursus/:cursus_id/skills` | 🌐 |
| GET | `/v2/skills` | 🌐 |
| GET | `/v2/skills/:id` | 🌐 |
| GET | `/v2/skills/:id` | 🌐 |
| POST | `/v2/skills` | 🔒 |
| POST | `/v2/skills` | 🔒 |
| PATCH | `/v2/skills/:id` | 🔒 |
| PUT | `/v2/skills/:id` | 🔒 |
| PATCH | `/v2/skills/:id` | 🔒 |
| PUT | `/v2/skills/:id` | 🔒 |
| DELETE | `/v2/skills/:id` | 🔒 |
| DELETE | `/v2/skills/:id` | 🔒 |

## Slots The slots available to users for booking a project scale team.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/slots/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/projects/:project_id/slots/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/users/:user_id/slots/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/slots` | 🌐 |
| GET | `/v2/projects/:project_id/slots` | 🌐 |
| GET | `/v2/users/:user_id/slots` | 🌐 |
| GET | `/v2/me/slots` | 🌐 |
| GET | `/v2/slots/:id` | 🌐 |
| POST | `/v2/slots` | 🔒 |
| PATCH | `/v2/slots/:id` | 🔒 |
| PUT | `/v2/slots/:id` | 🔒 |
| DELETE | `/v2/slots/:id` | 🔒 |

## Squads A squads is the managing container of squads_users.

| Metodo | Path | Acesso |
|--------|------|--------|
| POST | `/v2/blocs/:bloc_id/squads` | 🔒 |
| DELETE | `/v2/blocs/:bloc_id/squads/:id` | 🔒 |
| DELETE | `/v2/squads/:id` | 🔒 |
| GET | `/v2/blocs/:bloc_id/squads` | 🔒 |
| GET | `/v2/blocs/:bloc_id/squads/:id` | 🔒 |
| GET | `/v2/squads/:id` | 🔒 |
| PATCH | `/v2/squads/:id` | 🔒 |
| PUT | `/v2/squads/:id` | 🔒 |

## Squads users A squads_users will group users inside a same coalition

| Metodo | Path | Acesso |
|--------|------|--------|
| POST | `/v2/blocs/:bloc_id/squads_users` | 🔒 |
| DELETE | `/v2/blocs/:bloc_id/squads_users/:id` | 🔒 |
| DELETE | `/v2/squads_users/:id` | 🔒 |
| GET | `/v2/blocs/:bloc_id/squads_users` | 🔒 |
| PATCH | `/v2/squads_users/:id` | 🔒 |
| PUT | `/v2/squads_users/:id` | 🔒 |

## Subnotions The elearning subnotion in a notion

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/notions/:notion_id/subnotions` | 🌐 |
| GET | `/v2/subnotions` | 🌐 |
| GET | `/v2/subnotions/:id` | 🌐 |
| POST | `/v2/subnotions` | 🔒 |
| PATCH | `/v2/subnotions/:id` | 🔒 |
| PUT | `/v2/subnotions/:id` | 🔒 |
| DELETE | `/v2/subnotions/:id` | 🔒 |

## Tags Non-hierarchical keyword, acting as a meta-data and helping to describe entities.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/projects/:project_id/tags` | 🌐 |
| GET | `/v2/issues/:issue_id/tags` | 🌐 |
| GET | `/v2/notions/:notion_id/tags` | 🌐 |
| GET | `/v2/cursus/:cursus_id/tags` | 🌐 |
| GET | `/v2/users/:user_id/tags` | 🌐 |
| GET | `/v2/tags` | 🌐 |
| GET | `/v2/tags/:id` | 🌐 |
| POST | `/v2/tags` | 🔒 |
| PATCH | `/v2/tags/:id` | 🔒 |
| PUT | `/v2/tags/:id` | 🔒 |
| DELETE | `/v2/tags/:id` | 🔒 |

## Tags users Resource associating a User and a Tag.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/tags_users` | 🌐 |
| GET | `/v2/users/:user_id/tags_users` | 🌐 |
| GET | `/v2/cursus/:cursus_id/tags_users` | 🌐 |
| GET | `/v2/campus/:campus_id/tags_users` | 🌐 |
| GET | `/v2/tags/:tag_id/tags_users` | 🌐 |
| GET | `/v2/tags_users/:id` | 🌐 |
| POST | `/v2/tags_users` | 🔒 |
| PATCH | `/v2/tags_users/:id` | 🔒 |
| PUT | `/v2/tags_users/:id` | 🔒 |
| DELETE | `/v2/tags_users/:id` | 🔒 |

## Teams One or many users which have to finish a project together.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/cursus/:cursus_id/teams/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/users/:user_id/teams/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/users/:user_id/projects/:project_id/teams/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/teams/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/projects/:project_id/teams/graph(/on/:field(/by/:interval))` | 🌐 |
| GET | `/v2/cursus/:cursus_id/teams` | 🌐 |
| GET | `/v2/users/:user_id/teams` | 🌐 |
| GET | `/v2/users/:user_id/projects/:project_id/teams` | 🌐 |
| GET | `/v2/teams` | 🌐 |
| GET | `/v2/projects/:project_id/teams` | 🌐 |
| GET | `/v2/project_sessions/:project_session_id/teams` | 🌐 |
| GET | `/v2/me/teams` | 🌐 |
| GET | `/v2/teams/:id` | 🌐 |
| POST | `/v2/teams` | 🔒 |
| PATCH | `/v2/teams/:id` | 🔒 |
| PUT | `/v2/teams/:id` | 🔒 |
| DELETE | `/v2/teams/:id` | 🔒 |
| POST | `/v2/teams/:id/reset_team_uploads` | 🔒 |

## Teams uploads An uploaded mark for a team, given by a bot (like the Moulinette), without any defence.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/teams/:team_id/teams_uploads` | 🌐 |
| GET | `/v2/teams_uploads` | 🌐 |
| GET | `/v2/teams_uploads/:id` | 🌐 |
| POST | `/v2/teams_uploads` | 🔒 |
| PATCH | `/v2/teams_uploads/:id` | 🔒 |
| PUT | `/v2/teams_uploads/:id` | 🔒 |
| DELETE | `/v2/teams_uploads/:id` | 🔒 |
| POST | `/v2/teams_uploads/multiple_create` | 🔒 |

## Teams users Team composed of one User

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/teams_users` | 🌐 |
| GET | `/v2/users/:user_id/teams_users` | 🌐 |
| GET | `/v2/teams/:team_id/teams_users` | 🌐 |
| GET | `/v2/teams_users/:id` | 🌐 |
| POST | `/v2/teams_users` | 🔒 |
| PATCH | `/v2/teams_users/:id` | 🔒 |
| PUT | `/v2/teams_users/:id` | 🔒 |
| DELETE | `/v2/teams_users/:id` | 🔒 |

## Titles Titles a user can obtain, generally through achievements. It will be displayed on their profile and on the forum.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/titles` | 🌐 |
| GET | `/v2/users/:user_id/titles` | 🌐 |
| GET | `/v2/titles/:id` | 🌐 |
| POST | `/v2/titles` | 🔒 |
| PATCH | `/v2/titles/:id` | 🔒 |
| PUT | `/v2/titles/:id` | 🔒 |
| DELETE | `/v2/titles/:id` | 🔒 |

## Titles users Users who have a title.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/titles/:title_id/titles_users` | 🌐 |
| GET | `/v2/users/:user_id/titles_users` | 🌐 |
| GET | `/v2/titles_users` | 🌐 |
| GET | `/v2/titles_users/:id` | 🌐 |
| POST | `/v2/titles_users` | 🔒 |
| PATCH | `/v2/titles_users/:id` | 🔒 |
| PUT | `/v2/titles_users/:id` | 🔒 |
| DELETE | `/v2/titles_users/:id` | 🔒 |

## Transactions Transaction represents Altarian Dollars earned.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/transactions` | 🔒 |
| GET | `/v2/users/:user_id/transactions` | 🔒 |
| GET | `/v2/transactions/:id` | 🔒 |
| POST | `/v2/transactions` | 🔒 |
| DELETE | `/v2/transactions/:id` | 🔒 |

## Translations Translations

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/translations` | 🌐 |
| GET | `/v2/translations/:id` | 🌐 |
| POST | `/v2/translations` | 🔒 |
| PATCH | `/v2/translations/:id` | 🔒 |
| PUT | `/v2/translations/:id` | 🔒 |
| DELETE | `/v2/translations/:id` | 🔒 |
| POST | `/v2/translations/upload` | 🔒 |

## User candidatures The candidature of an user

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/user_candidatures` | 🔒 |
| GET | `/v2/users/:user_id/user_candidature` | 🔒 |
| GET | `/v2/user_candidatures/:id` | 🔒 |
| POST | `/v2/users/:user_id/user_candidature` | 🔒 |
| POST | `/v2/user_candidatures` | 🔒 |
| PATCH | `/v2/users/:user_id/user_candidature` | 🔒 |
| PUT | `/v2/users/:user_id/user_candidature` | 🔒 |
| PATCH | `/v2/user_candidatures/:id` | 🔒 |
| PUT | `/v2/user_candidatures/:id` | 🔒 |

## Users A 42 student, staff, or any entity with a 42 account.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/users/graph(/on/:field(/by/:interval))` | 🌐 |
| POST | `/v2/users/:id/correction_points/add` | 🔒 |
| DELETE | `/v2/users/:id/correction_points/remove` | 🔒 |
| GET | `/v2/users/:id/locations_stats` | 🌐 |
| GET | `/v2/users/:id/exam` | 🔒 |
| GET | `/v2/coalitions/:coalition_id/users` | 🌐 |
| GET | `/v2/dashes/:dash_id/users` | 🌐 |
| GET | `/v2/events/:event_id/users` | 🌐 |
| GET | `/v2/accreditations/:accreditation_id/users` | 🌐 |
| GET | `/v2/teams/:team_id/users` | 🌐 |
| GET | `/v2/projects/:project_id/users` | 🌐 |
| GET | `/v2/partnerships/:partnership_id/users` | 🌐 |
| GET | `/v2/expertises/:expertise_id/users` | 🌐 |
| GET | `/v2/users` | 🌐 |
| GET | `/v2/cursus/:cursus_id/users` | 🌐 |
| GET | `/v2/campus/:campus_id/users` | 🌐 |
| GET | `/v2/achievements/:achievement_id/users` | 🌐 |
| GET | `/v2/titles/:title_id/users` | 🌐 |
| GET | `/v2/quests/:quest_id/users` | 🌐 |
| GET | `/v2/groups/:group_id/users` | 🌐 |
| GET | `/v2/users/:id` | 🌐 |
| POST | `/v2/users` | 🔒 |
| PATCH | `/v2/users/:id` | 🔒 |
| PUT | `/v2/users/:id` | 🔒 |
| GET | `/v2/me` | 🌐 |
| POST | `/v2/users/:id/free_past_agu` | 🔒 |
| POST | `/v2/users/:user_id/unfreeze` | 🔒 |
| POST | `/v2/users/:id/set_primary_campus` | 🔒 |
| POST | `/v2/users/:id/alumnize` | 🔒 |
| POST | `/v2/users/:id/dealumnize` | 🔒 |
| DELETE | `/v2/users/:id/otp_settings/remove` | 🔒 |
| GET | `/v2/staff` | 🔒 |
| GET | `/v2/users/:user_id/projects_users/registration` | 🌐 |

## Waitlists Waitlist for an event or an exam.

| Metodo | Path | Acesso |
|--------|------|--------|
| GET | `/v2/waitlists` | 🔒 |
| GET | `/v2/events/:event_id/waitlist` | 🔒 |
| GET | `/v2/exams/:exam_id/waitlist` | 🔒 |
| GET | `/v2/waitlists/:id` | 🔒 |
| DELETE | `/v2/waitlists/:id` | 🔒 |

## Webhook registeries Webhook Registeries

| Metodo | Path | Acesso |
|--------|------|--------|
| POST | `/v2/webhook_registeries/:id/deactivate` | 🔒 |
