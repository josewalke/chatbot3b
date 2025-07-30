<?php
/**
 * Plugin Name: Chatbot Inteligente Optimizado
 * Plugin URI: https://github.com/tu-usuario/chatbot-inteligente
 * Description: Chatbot gratuito y optimizado para WordPress con capacidades de agendamiento, ventas y atención al cliente.
 * Version: 2.0.0
 * Author: Tu Nombre
 * License: GPL v2 or later
 * Text Domain: chatbot-optimized
 */

// Prevenir acceso directo
if (!defined('ABSPATH')) {
    exit;
}

// Definir constantes optimizadas
define('CHATBOT_OPTIMIZED_URL', plugin_dir_url(__FILE__));
define('CHATBOT_OPTIMIZED_PATH', plugin_dir_path(__FILE__));
define('CHATBOT_OPTIMIZED_VERSION', '2.0.0');

/**
 * Clase principal del plugin optimizado
 */
class ChatbotOptimized {
    
    private $api_url;
    private $cache_timeout;
    private $debug_mode;
    
    public function __construct() {
        // Configuración optimizada
        $this->api_url = get_option('chatbot_api_url', 'http://localhost:8000');
        $this->cache_timeout = 300; // 5 minutos
        $this->debug_mode = false; // Desactivar debug para ahorrar recursos
        
        $this->init_hooks();
    }
    
    private function init_hooks() {
        // Hooks optimizados - solo los esenciales
        add_action('init', array($this, 'init'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_action('wp_ajax_chatbot_send_message', array($this, 'ajax_send_message'));
        add_action('wp_ajax_nopriv_chatbot_send_message', array($this, 'ajax_send_message'));
        add_action('wp_ajax_chatbot_create_appointment', array($this, 'ajax_create_appointment'));
        add_action('wp_ajax_nopriv_chatbot_create_appointment', array($this, 'ajax_create_appointment'));
        
        // Shortcodes optimizados
        add_shortcode('chatbot', array($this, 'chatbot_shortcode'));
        add_shortcode('chatbot_widget', array($this, 'chatbot_widget_shortcode'));
        
        // Menú de administración simplificado
        add_action('admin_menu', array($this, 'admin_menu'));
        
        // Activación y desactivación
        register_activation_hook(__FILE__, array($this, 'activate'));
        register_deactivation_hook(__FILE__, array($this, 'deactivate'));
    }
    
    /**
     * Inicializar plugin optimizado
     */
    public function init() {
        // Cargar traducciones solo si es necesario
        if (is_admin()) {
            load_plugin_textdomain('chatbot-optimized', false, dirname(plugin_basename(__FILE__)) . '/languages');
        }
    }
    
    /**
     * Cargar scripts y estilos optimizados
     */
    public function enqueue_scripts() {
        // Solo cargar en páginas que lo necesiten
        if ($this->should_load_chatbot()) {
            wp_enqueue_style('chatbot-optimized-style', CHATBOT_OPTIMIZED_URL . 'assets/css/chatbot-optimized.css', array(), CHATBOT_OPTIMIZED_VERSION);
            wp_enqueue_script('chatbot-optimized-script', CHATBOT_OPTIMIZED_URL . 'assets/js/chatbot-optimized.js', array('jquery'), CHATBOT_OPTIMIZED_VERSION, true);
            
            // Localizar script con datos mínimos
            wp_localize_script('chatbot-optimized-script', 'chatbot_optimized', array(
                'ajax_url' => admin_url('admin-ajax.php'),
                'nonce' => wp_create_nonce('chatbot_optimized_nonce'),
                'api_url' => $this->api_url,
                'user_id' => $this->get_user_id(),
                'debug' => $this->debug_mode
            ));
        }
    }
    
    /**
     * Verificar si debe cargar el chatbot
     */
    private function should_load_chatbot() {
        // Solo cargar en páginas específicas o si hay shortcode
        global $post;
        if ($post && (
            has_shortcode($post->post_content, 'chatbot') ||
            has_shortcode($post->post_content, 'chatbot_widget') ||
            is_front_page() ||
            is_page()
        )) {
            return true;
        }
        return false;
    }
    
    /**
     * Obtener ID de usuario optimizado
     */
    private function get_user_id() {
        if (is_user_logged_in()) {
            return 'user_' . get_current_user_id();
        }
        return 'guest_' . substr(md5($_SERVER['REMOTE_ADDR']), 0, 8);
    }
    
    /**
     * AJAX: Enviar mensaje optimizado
     */
    public function ajax_send_message() {
        check_ajax_referer('chatbot_optimized_nonce', 'nonce');
        
        $user_id = sanitize_text_field($_POST['user_id']);
        $message = sanitize_textarea_field($_POST['message']);
        $platform = sanitize_text_field($_POST['platform']);
        
        // Validación básica
        if (empty($message)) {
            wp_send_json_error('Mensaje vacío');
            return;
        }
        
        // Llamada a API optimizada
        $response = $this->call_api('POST', '/chat/send', array(
            'user_id' => $user_id,
            'message' => $message,
            'platform' => $platform
        ));
        
        if ($response && isset($response['success']) && $response['success']) {
            wp_send_json_success($response);
        } else {
            wp_send_json_error('Error en el servidor');
        }
    }
    
    /**
     * AJAX: Crear cita optimizada
     */
    public function ajax_create_appointment() {
        check_ajax_referer('chatbot_optimized_nonce', 'nonce');
        
        $user_id = sanitize_text_field($_POST['user_id']);
        $service_type = sanitize_text_field($_POST['service_type']);
        $date = sanitize_text_field($_POST['date']);
        $time = sanitize_text_field($_POST['time']);
        
        // Validación básica
        if (empty($user_id) || empty($service_type) || empty($date) || empty($time)) {
            wp_send_json_error('Datos incompletos');
            return;
        }
        
        // Llamada a API optimizada
        $response = $this->call_api('POST', '/appointments/create', array(
            'user_id' => $user_id,
            'service_type' => $service_type,
            'date' => $date,
            'time' => $time
        ));
        
        if ($response && isset($response['success']) && $response['success']) {
            wp_send_json_success($response);
        } else {
            wp_send_json_error('Error creando cita');
        }
    }
    
    /**
     * Llamada a API optimizada con cache
     */
    private function call_api($method, $endpoint, $data = null) {
        $cache_key = 'chatbot_api_' . md5($method . $endpoint . serialize($data));
        
        // Intentar obtener del cache
        $cached_response = get_transient($cache_key);
        if ($cached_response !== false) {
            return $cached_response;
        }
        
        // Llamada a API
        $url = $this->api_url . $endpoint;
        $args = array(
            'method' => $method,
            'timeout' => 10,
            'headers' => array(
                'Content-Type' => 'application/json',
                'User-Agent' => 'Chatbot-Optimized/2.0.0'
            )
        );
        
        if ($data) {
            $args['body'] = json_encode($data);
        }
        
        $response = wp_remote_request($url, $args);
        
        if (is_wp_error($response)) {
            return false;
        }
        
        $body = wp_remote_retrieve_body($response);
        $result = json_decode($body, true);
        
        // Guardar en cache solo si es exitoso
        if ($result && isset($result['success']) && $result['success']) {
            set_transient($cache_key, $result, $this->cache_timeout);
        }
        
        return $result;
    }
    
    /**
     * Shortcode optimizado para chatbot
     */
    public function chatbot_shortcode($atts) {
        $atts = shortcode_atts(array(
            'theme' => 'light',
            'position' => 'bottom-right',
            'width' => '350',
            'height' => '500'
        ), $atts);
        
        ob_start();
        ?>
        <div id="chatbot-optimized" 
             data-theme="<?php echo esc_attr($atts['theme']); ?>"
             data-position="<?php echo esc_attr($atts['position']); ?>"
             style="width: <?php echo esc_attr($atts['width']); ?>px; height: <?php echo esc_attr($atts['height']); ?>px;">
            <div class="chatbot-header">
                <h3>🤖 Chatbot Inteligente</h3>
                <button class="chatbot-close">×</button>
            </div>
            <div class="chatbot-messages"></div>
            <div class="chatbot-input">
                <input type="text" placeholder="Escribe tu mensaje..." />
                <button class="chatbot-send">Enviar</button>
            </div>
        </div>
        <?php
        return ob_get_clean();
    }
    
    /**
     * Shortcode optimizado para widget
     */
    public function chatbot_widget_shortcode($atts) {
        $atts = shortcode_atts(array(
            'title' => 'Chatbot Inteligente',
            'show_online' => 'true'
        ), $atts);
        
        ob_start();
        ?>
        <div class="chatbot-widget">
            <h4><?php echo esc_html($atts['title']); ?></h4>
            <?php if ($atts['show_online'] === 'true'): ?>
                <p class="status online">🟢 En línea</p>
            <?php endif; ?>
            <button class="chatbot-open">💬 Iniciar Chat</button>
        </div>
        <?php
        return ob_get_clean();
    }
    
    /**
     * Menú de administración simplificado
     */
    public function admin_menu() {
        add_menu_page(
            'Chatbot Optimizado',
            'Chatbot',
            'manage_options',
            'chatbot-optimized',
            array($this, 'admin_page'),
            'dashicons-format-chat',
            30
        );
    }
    
    /**
     * Página de administración optimizada
     */
    public function admin_page() {
        ?>
        <div class="wrap">
            <h1>🤖 Chatbot Inteligente Optimizado</h1>
            
            <div class="chatbot-admin-grid">
                <div class="chatbot-admin-card">
                    <h3>📊 Estado del Servidor</h3>
                    <div id="server-status">
                        <p>Verificando...</p>
                    </div>
                </div>
                
                <div class="chatbot-admin-card">
                    <h3>⚙️ Configuración</h3>
                    <form method="post" action="options.php">
                        <?php settings_fields('chatbot_optimized_options'); ?>
                        <table class="form-table">
                            <tr>
                                <th>URL del API:</th>
                                <td>
                                    <input type="url" name="chatbot_api_url" 
                                           value="<?php echo esc_attr(get_option('chatbot_api_url', 'http://localhost:8000')); ?>" 
                                           class="regular-text" />
                                </td>
                            </tr>
                        </table>
                        <?php submit_button(); ?>
                    </form>
                </div>
                
                <div class="chatbot-admin-card">
                    <h3>📈 Estadísticas</h3>
                    <div id="chatbot-stats">
                        <p>Cargando...</p>
                    </div>
                </div>
            </div>
            
            <div class="chatbot-admin-info">
                <h3>💡 Información de Optimización</h3>
                <ul>
                    <li>✅ Cache optimizado (5 minutos)</li>
                    <li>✅ Carga condicional de scripts</li>
                    <li>✅ Validación de datos</li>
                    <li>✅ Timeouts configurados</li>
                    <li>✅ Logging mínimo</li>
                </ul>
            </div>
        </div>
        
        <script>
        jQuery(document).ready(function($) {
            // Verificar estado del servidor
            $.get('<?php echo esc_url($this->api_url); ?>/health')
                .done(function(data) {
                    $('#server-status').html('<p style="color: green;">🟢 Servidor funcionando</p>');
                })
                .fail(function() {
                    $('#server-status').html('<p style="color: red;">🔴 Servidor no disponible</p>');
                });
            
            // Cargar estadísticas
            $.get('<?php echo esc_url($this->api_url); ?>/stats')
                .done(function(data) {
                    $('#chatbot-stats').html(`
                        <p>👥 Usuarios: ${data.users || 0}</p>
                        <p>💬 Conversaciones: ${data.conversations || 0}</p>
                        <p>📅 Citas: ${data.appointments || 0}</p>
                    `);
                })
                .fail(function() {
                    $('#chatbot-stats').html('<p>No se pueden cargar las estadísticas</p>');
                });
        });
        </script>
        <?php
    }
    
    /**
     * Activación optimizada
     */
    public function activate() {
        // Configuraciones por defecto
        add_option('chatbot_api_url', 'http://localhost:8000');
        add_option('chatbot_optimized_version', CHATBOT_OPTIMIZED_VERSION);
        
        // Limpiar cache
        wp_cache_flush();
    }
    
    /**
     * Desactivación optimizada
     */
    public function deactivate() {
        // Limpiar cache
        wp_cache_flush();
        
        // Limpiar transients
        delete_transient('chatbot_api_*');
    }
}

// Inicializar plugin optimizado
new ChatbotOptimized();

// Registrar opciones
add_action('admin_init', function() {
    register_setting('chatbot_optimized_options', 'chatbot_api_url');
}); 