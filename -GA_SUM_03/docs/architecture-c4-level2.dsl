workspace "TiendaTech Microservices" "Architecture for TiendaTech" {

    model {
        user = person "User / Client" "A customer or client application."

        tiendaTech = softwareSystem "TiendaTech System" "E-commerce and resource management platform." {
            apiGateway = container "API Gateway" "Routes incoming API requests." "Nginx" {
                tags "Gateway"
            }
            
            authService = container "Auth Service" "Handles user authentication." "Spring Boot, Java" {
                tags "Microservice"
            }
            authDb = container "Auth Database" "Stores users and roles." "PostgreSQL" {
                tags "Database"
            }
            
            resourceService = container "Resource Service" "Handles product catalogs." "Spring Boot, Java" {
                tags "Microservice"
            }
            resourceDb = container "Resource Database" "Stores product data." "PostgreSQL" {
                tags "Database"
            }
            
            notificationService = container "Notification Service" "Sends alerts." "Spring Boot, Java" {
                tags "Microservice"
            }
        }

        smtp = softwareSystem "External SMTP Server" "Sends emails." {
            tags "External"
        }

        user -> apiGateway "Makes API requests to"
        
        apiGateway -> authService "Routes to /api/auth/"
        apiGateway -> resourceService "Routes to /api/resources/"
        apiGateway -> notificationService "Routes to /api/notifications/"

        authService -> authDb "Reads/Writes [JDBC]"
        resourceService -> resourceDb "Reads/Writes [JDBC]"
        
        notificationService -> smtp "Sends emails [SMTP]"
    }

    views {
        container tiendaTech "Containers" {
            include *
            autoLayout
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
        }
    }
}