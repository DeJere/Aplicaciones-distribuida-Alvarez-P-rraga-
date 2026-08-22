workspace "TiendaTech - C4 Nivel 3" "Diagrama de componentes internos de cada microservicio" {

    model {
        user = person "Usuario / Cliente" "Cliente que consume la API."

        tiendaTech = softwareSystem "TiendaTech System" {

            apiGateway = container "API Gateway" "Enruta peticiones y aplica rate limiting." "Nginx" {
                tags "Gateway"
            }

            # ── Auth Service ──────────────────────────────────────
            authService = container "Auth Service" "Autenticación y emisión de JWT." "Spring Boot 3 / Java 21" {
                tags "Microservice"

                authController = component "AuthController" "Expone /register, /login, /validate." "REST Controller"
                authServiceComp = component "AuthService" "Lógica de registro, login y validación." "Spring Service"
                jwtProvider = component "JwtTokenProvider" "Genera y valida tokens JWT (HS512)." "Spring Component"
                userDetailsService = component "CustomUserDetailsService" "Carga usuario desde DB para Spring Security." "Spring Service"
                securityConfig = component "SecurityConfig" "Configura filtros y reglas de seguridad." "Spring Configuration"
                jwtFilter = component "JwtAuthenticationFilter" "Valida JWT en cada petición." "OncePerRequestFilter"
                userRepo = component "UserRepository" "Acceso a tabla users." "JPA Repository"

                authController -> authServiceComp "Delega lógica"
                authServiceComp -> jwtProvider "Genera/valida token"
                authServiceComp -> userRepo "Busca/guarda usuario"
                jwtFilter -> jwtProvider "Valida token entrante"
                userDetailsService -> userRepo "Carga detalles de usuario"
                securityConfig -> jwtFilter "Registra filtro"
                securityConfig -> userDetailsService "Configura UserDetailsService"
            }

            authDb = container "Auth Database" "Almacena usuarios y roles." "PostgreSQL 15" {
                tags "Database"
            }

            # ── Resource Service ──────────────────────────────────
            resourceService = container "Resource Service" "CRUD de productos con protección JWT." "Spring Boot 3 / Java 21" {
                tags "Microservice"

                productController = component "ProductController" "Expone CRUD en /." "REST Controller"
                productServiceComp = component "ProductService" "Lógica CRUD con notificaciones." "Spring Service"
                notifClient = component "NotificationClient" "Llama al Notification Service vía HTTP." "Spring Component"
                jwtInterceptor = component "JwtInterceptor" "Intercepta peticiones y valida JWT." "HandlerInterceptor"
                jwtValidator = component "JwtValidator" "Decodifica y verifica firma JWT." "Spring Component"
                productRepo = component "ProductRepository" "Acceso a tabla products." "JPA Repository"

                productController -> productServiceComp "Delega CRUD"
                productServiceComp -> productRepo "Persistencia"
                productServiceComp -> notifClient "Envía evento tras create/update/delete"
                jwtInterceptor -> jwtValidator "Valida token"
            }

            resourceDb = container "Resource Database" "Almacena catálogo de productos." "PostgreSQL 15" {
                tags "Database"
            }

            # ── Notification Service ───────────────────────────────
            notificationService = container "Notification Service" "Registra eventos y simula envío de email." "Spring Boot 3 / Java 21" {
                tags "Microservice"

                notifController = component "NotificationController" "Expone POST /notifications y GET /notifications." "REST Controller"
                notifServiceComp = component "NotificationService" "Persiste log y simula SMTP." "Spring Service"
                notifRepo = component "NotificationLogRepository" "Acceso a tabla notification_logs." "JPA Repository"

                notifController -> notifServiceComp "Procesa evento"
                notifServiceComp -> notifRepo "Persiste NotificationLog"
            }

            notifDb = container "Notification Database" "Almacena historial de notificaciones." "PostgreSQL 15" {
                tags "Database"
            }
        }

        smtp = softwareSystem "Servidor SMTP Externo" "Envía correos electrónicos." {
            tags "External"
        }

        # Relaciones externas
        user -> apiGateway "HTTPS / REST"
        apiGateway -> authService "→ /api/auth/*"
        apiGateway -> resourceService "→ /api/resources/*"
        apiGateway -> notificationService "→ /api/notifications/*"

        authService -> authDb "JDBC"
        resourceService -> resourceDb "JDBC"
        resourceService -> notificationService "HTTP POST /notifications"
        notificationService -> notifDb "JDBC"
        notifServiceComp -> smtp "SMTP (simulado en logs)"
    }

    views {
        # Vista nivel 2 - Contenedores
        container tiendaTech "C4-Level2-Containers" {
            include *
            autoLayout
            title "TiendaTech - Nivel 2: Contenedores"
        }

        # Vistas nivel 3 - Componentes por microservicio
        component authService "C4-Level3-AuthService" {
            include *
            autoLayout
            title "Auth Service - Nivel 3: Componentes"
        }

        component resourceService "C4-Level3-ResourceService" {
            include *
            autoLayout
            title "Resource Service - Nivel 3: Componentes"
        }

        component notificationService "C4-Level3-NotificationService" {
            include *
            autoLayout
            title "Notification Service - Nivel 3: Componentes"
        }

        styles {
            element "Person" {
                background #08427b
                color #ffffff
                shape Person
            }
            element "Microservice" {
                background #438dd5
                color #ffffff
                shape RoundedBox
            }
            element "Gateway" {
                background #1168bd
                color #ffffff
                shape Hexagon
            }
            element "Database" {
                background #2d882d
                color #ffffff
                shape Cylinder
            }
            element "External" {
                background #999999
                color #ffffff
                shape RoundedBox
            }
            element "Component" {
                background #85bbf0
                color #000000
            }
        }
    }
}
