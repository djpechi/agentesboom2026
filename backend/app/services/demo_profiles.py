# /backend/app/services/demo_profiles.py

DEMO_PROFILES = {
    "saas_b2b": {
        "name": "SaaS B2B - CRM para Startups",
        "company_name": "TechFlow CRM",
        "profile": """
        Empresa: TechFlow CRM
        Industria: SaaS B2B
        Producto: CRM especializado para startups tecnológicas
        Tamaño: 50-200 empleados
        Revenue: $2M-$5M ARR
        Mercado objetivo: Startups Serie A/B en tecnología
        Geografía: Estados Unidos y Canadá
        Competidores: HubSpot, Pipedrive, Salesforce
        Diferenciador: Integración nativa con herramientas de desarrollo (GitHub, Jira)
        Pain points del cliente: Falta de visibilidad del pipeline, procesos manuales
        Objetivos: Aumentar MRR 30%, reducir churn a <5%
        Website: https://techflowcrm.com
        """,
        "stage_specific": {
            1: {  # Agente 1: Booms
                "buyer_persona_name": "Carlos, VP de Operaciones en Startup Serie B",
                "buyer_age": "35-45 años",
                "decision_makers": "VP Ops, CTO, CEO",
                "buying_triggers": "Rondas de inversión, crecimiento rápido del equipo"
            },
            2: {  # Agente 2: Journey
                "awareness_channels": ["LinkedIn", "Product Hunt", "Podcasts tech"],
                "consideration_content": ["Comparativas vs HubSpot", "ROI calculators"],
                "decision_factors": ["Facilidad de integración", "Precio", "Soporte"]
            },
            3: {  # Agente 3: Ofertas
                "dream_outcome": "Tener visibilidad total del pipeline sin esfuerzo manual",
                "time_delay": "Implementación en 24 horas",
                "effort_sacrifice": "Migración automática desde Excel/Pipedrive",
                "guarantee": "Devolución del 100% si no aumentas leads en 30 días"
            },
            4: {  # Agente 4: Canales
                "budget": "$5,000 USD mensuales",
                "team": "Equipo interno pequeño (1 marketer, 1 diseñador)",
                "assets": "Lista de correos de 2,000 contactos, Blog activo",
                "timeline": "Resultados en 3 meses"
            },
            5: {  # Agente 5: Atlas
                "book_chapters": ["Gestión de Proyectos Ágil", "Liderazgo Remoto", "Productividad Personal"],
                "missing_content": "Guías reales de cómo implementar procesos, no solo teoría."
            },
            6: {  # Agente 6: Planner
                "max_velocity": "2 posts de blog al mes, 3 posts de LinkedIn a la semana",
                "team_capacity": "1 redactor freelance a medio tiempo"
            },
            7: {  # Agente 7: Budgets
                # Budget is often inherited from Stage 4 context, but we can override or add specific finance constraints
                "financial_constraints": "Costo de adquisición máximo permitido: $50 USD",
                "cashflow_constraints": "Pago mensual con tarjeta de crédito corporativa"
            }
        }
    },

    "ecommerce": {
        "name": "E-commerce - Moda Sostenible",
        "company_name": "GreenThreads",
        "profile": """
        Empresa: GreenThreads
        Industria: E-commerce / Moda
        Producto: Ropa sostenible y eco-friendly
        Tamaño: 10-50 empleados
        Revenue: $500K-$2M
        Mercado objetivo: Millennials y Gen Z conscientes del medio ambiente
        Geografía: México y Latinoamérica
        Competidores: Patagonia, Reformation, locales
        Diferenciador: 100% producción local con materiales reciclados
        Pain points del cliente: Precio, desconocimiento de impacto ambiental
        Objetivos: Aumentar conversión 20%, reducir CAC 15%
        Website: https://greenthreads.mx
        """,
        "stage_specific": {
            1: {
                "buyer_persona_name": "Ana, Profesional Millennial eco-consciente",
                "buyer_age": "28-35 años",
                "decision_makers": "Individual, influencia de redes sociales",
                "buying_triggers": "Tendencias de sostenibilidad, influencers"
            }
        }
    },

    "edenred": {
        "name": "Edenred México",
        "company_name": "Edenred México",
        "profile": """
        Empresa: Edenred México
        Industria: Fintech / Servicios Financieros / Vales de Despensa
        Producto: Vales de despensa, tarjetas de combustible, soluciones de beneficios para empleados
        Tamaño: Grande (1000+ empleados)
        Revenue: >$50M
        Mercado objetivo: Empresas medianas y grandes en México que buscan optimizar beneficios fiscales y prestaciones
        Geografía: Nivel nacional (México)
        Competidores: Sodexo, Si Vale, Up Sí Vale
        Diferenciador: Plataforma tecnológica robusta, amplia red de afiliados, app móvil intuitiva
        Pain points del cliente: Gestión administrativa compleja, deducibilidad fiscal, retención de talento
        Objetivos: Aumentar penetración en PyMEs, fidelizar grandes cuentas
        Website: https://www.edenred.mx
        """,
        "stage_specific": {
            1: {
                "buyer_persona_name": "Gerente de Recursos Humanos",
                "buyer_age": "35-50 años",
                "decision_makers": "Director de RH, Director Financiero (CFO)",
                "buying_triggers": "Reformas fiscales, necesidad de retener talento, simplificación administrativa"
            }
        }
    },

    "transmodal": {
        "name": "Transmodal",
        "company_name": "Transmodal",
        "profile": """
        Empresa: Transmodal
        Industria: Logística / Transporte Internacional
        Producto: Soluciones logísticas integrales, fletes marítimos, aéreos y terrestres
        Tamaño: Mediana (50-200 empleados)
        Revenue: $10M-$50M
        Mercado objetivo: Empresas importadoras y exportadoras en México (Manufactura, Retail)
        Geografía: México con alcance global
        Competidores: Kuhne+Nagel, DSV, Agencias de carga locales
        Diferenciador: Atención personalizada 24/7, visibilidad en tiempo real de la carga
        Pain points del cliente: Retrasos en aduanas, falta de visibilidad, costos ocultos
        Objetivos: Captar clientes de industria automotriz y farmacéutica
        Website: https://www.transmodal.com.mx
        """,
        "stage_specific": {
            1: {
                "buyer_persona_name": "Gerente de Logística / Importar-Exportar",
                "buyer_age": "30-45 años",
                "decision_makers": "Gerente de Supply Chain, Director de Operaciones",
                "buying_triggers": "Crisis en cadena de suministro, necesidad de reducir tiempos de tránsito"
            }
        }
    },

    "credifiel": {
        "name": "Credifiel",
        "company_name": "Credifiel",
        "profile": """
        Empresa: Credifiel
        Industria: Servicios Financieros / Créditos de Nómina
        Producto: Préstamos personales con descuento vía nómina para empleados de gobierno
        Tamaño: Grande (500+ empleados)
        Revenue: >$20M
        Mercado objetivo: Trabajadores del sector gobierno (SNTE, Salud, Gobierno)
        Geografía: México (Cobertura nacional)
        Competidores: Crédito Maestro, Kondinero
        Diferenciador: Rapidez en la aprobación, atención en sucursal y digital
        Pain points del cliente: Necesidad de liquidez inmediata, burocracia bancaria tradicional, sobreendeudamiento
        Objetivos: Colocación de créditos nuevos, refinanciamiento de cartera
        Website: https://www.credifiel.com.mx
        """,
        "stage_specific": {
            1: {
                "buyer_persona_name": "Trabajador de Gobierno Sindicalizado",
                "buyer_age": "40-60 años",
                "decision_makers": "Usuario final (decisión individual/familiar)",
                "buying_triggers": "Emergencias familiares, regreso a clases, gastos médicos"
            }
        }
    },

    "black_and_orange": {
        "name": "Black & Orange",
        "company_name": "Black & Orange",
        "profile": """
        Empresa: Black & Orange
        Industria: Marketing Digital / Agencia Inbound
        Producto: Estrategia Inbound, Implementación de CRM (HubSpot), Content Marketing
        Tamaño: Pequeña-Mediana (10-50 empleados)
        Revenue: $1M-$3M
        Mercado objetivo: Empresas B2B y Edu/Real Estate que quieren escalar ventas
        Geografía: México y Latam
        Competidores: Otras agencias Diamond/Platinum de HubSpot
        Diferenciador: Metodología probada, enfoque en resultados de venta (Revenue Operations)
        Pain points del cliente: Inversión en marketing sin ROI claro, desconexión entre marketing y ventas
        Objetivos: Atraer clientes que busquen implementación compleja de CRM y estrategia completa
        Website: https://blackandorange.mx
        """,
        "stage_specific": {
            1: {
                "buyer_persona_name": "Director Comercial / Dueño de Empresa",
                "buyer_age": "35-50 años",
                "decision_makers": "CEO, Director de Marketing",
                "buying_triggers": "Falta de crecimiento en ventas, CRM desordenado, necesidad de automatización"
            }
        }
    }
}
