-- ============================================================
-- SCHEMA SUPABASE - AGENCIA MARKETING IA
-- ============================================================
-- Estructura completa para sistema escalable multi-cliente

-- 1. CLIENTES
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    tipo_negocio VARCHAR(100),
    objetivo VARCHAR(100),
    publico_objetivo TEXT,
    presupuesto DECIMAL(10, 2),
    descripcion TEXT,
    logo_url TEXT,
    website TEXT,
    
    -- Aprendizaje del cliente
    tono_voz TEXT,
    valores_marca TEXT[],
    competidores TEXT[],
    preferencias_contenido JSONB,
    historial_interacciones JSONB DEFAULT '[]'::JSONB,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    estado VARCHAR(50) DEFAULT 'activo'
);

-- 2. CAMPAÑAS
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    nombre TEXT NOT NULL,
    objetivo_especifico TEXT,
    canal_principal VARCHAR(100),
    duracion_semanas INT,
    presupuesto DECIMAL(10, 2),
    target_metrics JSONB,
    
    -- Estado de campaña
    estado VARCHAR(50) DEFAULT 'draft', -- draft, approved, active, completed
    fecha_inicio DATE,
    fecha_fin DATE,
    
    -- Output de agentes (JSON completo)
    output_agentes JSONB,
    
    -- Feedback y mejoras
    feedback_cliente JSONB DEFAULT '{}'::JSONB,
    version INT DEFAULT 1,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

-- 3. RESPUESTAS DE AGENTES
CREATE TABLE agent_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    agent_type VARCHAR(50) NOT NULL, -- strategy, content, design, video, ads, automation
    
    -- Respuesta del agente
    data JSONB NOT NULL,
    reasoning TEXT,
    confidence DECIMAL(3, 2), -- 0.00 a 1.00
    
    -- Metadata
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

-- 4. HISTORIAL DE CAMPAÑAS (Para aprendizaje)
CREATE TABLE campaign_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(id),
    
    -- Qué pasó
    evento VARCHAR(100), -- generated, approved, launched, completed
    detalles JSONB,
    resultados JSONB, -- KPIs, metrics
    
    -- Fecha
    created_at TIMESTAMP DEFAULT now()
);

-- 5. FEEDBACK DE CLIENTE
CREATE TABLE client_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    
    -- Feedback
    agent_type VARCHAR(50), -- Qué agente
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comentario TEXT,
    mejoras_sugeridas TEXT[],
    
    -- Metadata
    created_at TIMESTAMP DEFAULT now()
);

-- 6. PREFERENCIAS DE CLIENTE (Para mejorar con cada campaña)
CREATE TABLE client_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL UNIQUE REFERENCES clients(id) ON DELETE CASCADE,
    
    -- Contenido
    temas_favoritos TEXT[],
    formatos_preferidos TEXT[], -- video, artículo, post, infografía
    plataformas_prioritarias TEXT[],
    
    -- Tono y estilo
    tono_voz VARCHAR(100),
    estilo_visual VARCHAR(100),
    valores_marca TEXT[],
    
    -- Márketing
    canales_efectivos TEXT[],
    cta_preferido VARCHAR(200),
    tipo_publicidad_efectiva TEXT[],
    
    -- CRM integración
    color_primario VARCHAR(7),
    color_secundario VARCHAR(7),
    fuentes_preferidas TEXT[],
    
    -- Metadata
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

-- 7. INTEGRACIONES (Para Meta, Google, etc)
CREATE TABLE integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    
    -- Plataforma
    platform VARCHAR(50) NOT NULL, -- meta, google, email, zapier, n8n
    estado VARCHAR(50) DEFAULT 'connected', -- connected, disconnected, error
    
    -- Credenciales (encriptadas)
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    
    -- Config
    configuracion JSONB, -- Config específica por plataforma
    
    -- Metadata
    connected_at TIMESTAMP DEFAULT now(),
    last_sync TIMESTAMP,
    sync_errors TEXT
);

-- 8. ACTIVACIONES (Para tracking de qué se activó)
CREATE TABLE activations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    
    -- Qué se activó
    tipo VARCHAR(100), -- email_campaign, facebook_ads, n8n_workflow, etc
    detalles JSONB,
    
    -- Estado
    estado VARCHAR(50) DEFAULT 'activated', -- activated, paused, error
    resultado JSONB, -- Response de API
    
    -- Metadata
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

-- 9. MÉTRICAS Y PERFORMANCE
CREATE TABLE campaign_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    
    -- Período
    fecha DATE,
    
    -- Métricas
    leads_generados INT DEFAULT 0,
    conversiones INT DEFAULT 0,
    clicks INT DEFAULT 0,
    impresiones INT DEFAULT 0,
    engagement_rate DECIMAL(5, 2),
    cpa_actual DECIMAL(10, 2),
    roi_actual DECIMAL(5, 2),
    
    -- Por canal
    canal VARCHAR(50),
    
    -- Metadata
    synced_at TIMESTAMP DEFAULT now()
);

-- 10. APRENDIZAJE DE AGENTES (Para mejorar con tiempo)
CREATE TABLE agent_learning (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    
    -- Qué aprendió
    agent_type VARCHAR(50),
    learning_type VARCHAR(100), -- content_preference, tone, format, etc
    data JSONB,
    
    -- Score de confianza
    confidence DECIMAL(3, 2),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

-- 11. TEMPLATES (Para reutilizar)
CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Metadata
    nombre TEXT NOT NULL,
    tipo_negocio VARCHAR(100),
    tipo_template VARCHAR(50), -- email, post, landing, workflow
    
    -- Contenido
    contenido JSONB,
    variables_disponibles TEXT[],
    
    -- Uso
    veces_usado INT DEFAULT 0,
    rating_promedio DECIMAL(3, 2),
    
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

-- 12. LOGS (Para debugging)
CREATE TABLE system_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(id),
    campaign_id UUID REFERENCES campaigns(id),
    
    -- Log
    nivel VARCHAR(20), -- INFO, WARNING, ERROR
    mensaje TEXT,
    datos JSONB,
    
    created_at TIMESTAMP DEFAULT now()
);

-- ============================================================
-- ÍNDICES PARA PERFORMANCE
-- ============================================================

CREATE INDEX idx_clients_email ON clients(email);
CREATE INDEX idx_campaigns_client ON campaigns(client_id);
CREATE INDEX idx_campaigns_estado ON campaigns(estado);
CREATE INDEX idx_agent_responses_campaign ON agent_responses(campaign_id);
CREATE INDEX idx_campaign_history_client ON campaign_history(client_id);
CREATE INDEX idx_integrations_client_platform ON integrations(client_id, platform);
CREATE INDEX idx_activations_campaign ON activations(campaign_id);
CREATE INDEX idx_metrics_campaign_fecha ON campaign_metrics(campaign_id, fecha);

-- ============================================================
-- FUNCIONES Y TRIGGERS
-- ============================================================

-- Función para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para clientes
CREATE TRIGGER update_clients_updated_at BEFORE UPDATE
    ON clients FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger para campañas
CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE
    ON campaigns FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- VISTAS ÚTILES
-- ============================================================

-- Vista: Clientes con sus campañas activas
CREATE VIEW client_campaigns_active AS
SELECT 
    c.id,
    c.nombre,
    COUNT(CASE WHEN camp.estado = 'active' THEN 1 END) as campanas_activas,
    SUM(camp.presupuesto) as presupuesto_total,
    MAX(camp.created_at) as ultima_campana
FROM clients c
LEFT JOIN campaigns camp ON c.id = camp.client_id
GROUP BY c.id;

-- Vista: Performance de campañas
CREATE VIEW campaign_performance AS
SELECT 
    c.id,
    c.nombre,
    camp.nombre as campana,
    SUM(CASE WHEN cm.leads_generados > 0 THEN cm.leads_generados ELSE 0 END) as leads_total,
    AVG(cm.cpa_actual) as cpa_promedio,
    AVG(cm.roi_actual) as roi_promedio
FROM clients c
JOIN campaigns camp ON c.id = camp.client_id
LEFT JOIN campaign_metrics cm ON camp.id = cm.campaign_id
GROUP BY c.id, camp.id;

-- ============================================================
-- POLÍTICAS DE SEGURIDAD (Row Level Security)
-- ============================================================

ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;

-- Política: Solo usuarios autenticados pueden ver sus propios datos
CREATE POLICY "Usuarios ven sus propios clientes"
    ON clients FOR SELECT
    USING (auth.uid()::text = client_id OR auth.role() = 'admin');

-- ============================================================
-- DATOS DE EJEMPLO (Para testing)
-- ============================================================

INSERT INTO clients (nombre, email, tipo_negocio, objetivo, publico_objetivo, presupuesto, descripcion)
VALUES 
    ('Dra. Mirle Noroño', 'mirle@example.com', 'Salud', 'Generar Leads', 'Mujeres 25-45', 500, 'Nutrióloga especializada');

INSERT INTO client_preferences (client_id, temas_favoritos, plataformas_prioritarias, tono_voz)
SELECT id, ARRAY['Nutrición', 'Salud', 'Bienestar'], ARRAY['Instagram', 'Email'], 'Educativo'
FROM clients WHERE email = 'mirle@example.com';

-- ============================================================
-- FIN DEL SCHEMA
-- ============================================================
