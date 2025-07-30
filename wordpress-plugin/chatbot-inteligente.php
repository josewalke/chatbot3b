<?php
/**
 * Plugin Name: Chatbot Inteligente
 * Plugin URI: https://github.com/tu-usuario/chatbot-inteligente
 * Description: Chatbot gratuito y completo para WordPress con capacidades de agendamiento, ventas y atención al cliente.
 * Version: 1.0.0
 * Author: Tu Nombre
 * License: GPL v2 or later
 * Text Domain: chatbot-inteligente
 */

// Prevenir acceso directo
if (!defined('ABSPATH')) {
    exit;
}

// Definir constantes
define('CHATBOT_PLUGIN_URL', plugin_dir_url(__FILE__));
define('CHATBOT_PLUGIN_PATH', plugin_dir_path(__FILE__));
define('CHATBOT_VERSION', '1.0.0');

/**
 * Clase principal del plugin
 */
class ChatbotInteligente {
    
    public function __construct() {
        add_action('init', array($this, 'init'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_action('admin_enqueue_scripts', array($this, 'admin_enqueue_scripts'));
        add_action('wp_ajax_chatbot_send_message', array($this, 'ajax_send_message'));
        add_action('wp_ajax_nopriv_chatbot_send_message', array($this, 'ajax_send_message'));
        add_action('wp_ajax_chatbot_create_appointment', array($this, 'ajax_create_appointment'));
        add_action('wp_ajax_nopriv_chatbot_create_appointment', array($this, 'ajax_create_appointment'));
        add_action('wp_ajax_chatbot_process_purchase', array($this, 'ajax_process_purchase'));
        add_action('wp_ajax_nopriv_chatbot_process_purchase', array($this, 'ajax_process_purchase'));
        
        // Registrar shortcodes
        add_shortcode('chatbot', array($this, 'chatbot_shortcode'));
        add_shortcode('chatbot_widget', array($this, 'chatbot_widget_shortcode'));
        
        // Registrar widgets
        add_action('widgets_init', array($this, 'register_widgets'));
        
        // Menú de administración
        add_action('admin_menu', array($this, 'admin_menu'));
        
        // Activación y desactivación
        register_activation_hook(__FILE__, array($this, 'activate'));
        register_deactivation_hook(__FILE__, array($this, 'deactivate'));
    }
    
    /**
     * Inicializar plugin
     */
    public function init() {
        // Cargar traducciones
        load_plugin_textdomain('chatbot-inteligente', false, dirname(plugin_basename(__FILE__)) . '/languages');
    }
    
    /**
     * Cargar scripts y estilos del frontend
     */
    public function enqueue_scripts() {
        wp_enqueue_style('chatbot-style', CHATBOT_PLUGIN_URL . 'assets/css/chatbot.css', array(), CHATBOT_VERSION);
        wp_enqueue_script('chatbot-script', CHATBOT_PLUGIN_URL . 'assets/js/chatbot.js', array('jquery'), CHATBOT_VERSION, true);
        
        // Localizar script
        wp_localize_script('chatbot-script', 'chatbot_ajax', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('chatbot_nonce'),
            'api_url' => get_option('chatbot_api_url', 'http://localhost:8000'),
            'user_id' => get_current_user_id() ?: 'guest_' . uniqid()
        ));
    }
    
    /**
     * Cargar scripts y estilos del admin
     */
    public function admin_enqueue_scripts($hook) {
        if (strpos($hook, 'chatbot') !== false) {
            wp_enqueue_style('chatbot-admin-style', CHATBOT_PLUGIN_URL . 'assets/css/admin.css', array(), CHATBOT_VERSION);
            wp_enqueue_script('chatbot-admin-script', CHATBOT_PLUGIN_URL . 'assets/js/admin.js', array('jquery'), CHATBOT_VERSION, true);
        }
    }
    
    /**
     * AJAX: Enviar mensaje
     */
    public function ajax_send_message() {
        check_ajax_referer('chatbot_nonce', 'nonce');
        
        $user_id = sanitize_text_field($_POST['user_id']);
        $message = sanitize_textarea_field($_POST['message']);
        $platform = sanitize_text_field($_POST['platform']);
        
        $api_url = get_option('chatbot_api_url', 'http://localhost:8000');
        $response = wp_remote_post($api_url . '/api/v1/chat/send', array(
            'body' => json_encode(array(
                'user_id' => $user_id,
                'message' => $message,
                'platform' => $platform
            )),
            'headers' => array('Content-Type' => 'application/json')
        ));
        
        if (is_wp_error($response)) {
            wp_send_json_error('Error de conexión');
        }
        
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        
        wp_send_json_success($data);
    }
    
    /**
     * AJAX: Crear cita
     */
    public function ajax_create_appointment() {
        check_ajax_referer('chatbot_nonce', 'nonce');
        
        $user_id = sanitize_text_field($_POST['user_id']);
        $appointment_data = array(
            'service_type' => sanitize_text_field($_POST['service_type']),
            'appointment_date' => sanitize_text_field($_POST['appointment_date']),
            'notes' => sanitize_textarea_field($_POST['notes'])
        );
        
        $api_url = get_option('chatbot_api_url', 'http://localhost:8000');
        $response = wp_remote_post($api_url . '/api/v1/appointments/create', array(
            'body' => json_encode(array(
                'user_id' => $user_id,
                'appointment' => $appointment_data
            )),
            'headers' => array('Content-Type' => 'application/json')
        ));
        
        if (is_wp_error($response)) {
            wp_send_json_error('Error de conexión');
        }
        
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        
        wp_send_json_success($data);
    }
    
    /**
     * AJAX: Procesar compra
     */
    public function ajax_process_purchase() {
        check_ajax_referer('chatbot_nonce', 'nonce');
        
        $user_id = sanitize_text_field($_POST['user_id']);
        $product_id = sanitize_text_field($_POST['product_id']);
        $quantity = intval($_POST['quantity']);
        
        $api_url = get_option('chatbot_api_url', 'http://localhost:8000');
        $response = wp_remote_post($api_url . '/api/v1/sales/purchase', array(
            'body' => json_encode(array(
                'user_id' => $user_id,
                'product_id' => $product_id,
                'quantity' => $quantity
            )),
            'headers' => array('Content-Type' => 'application/json')
        ));
        
        if (is_wp_error($response)) {
            wp_send_json_error('Error de conexión');
        }
        
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        
        wp_send_json_success($data);
    }
    
    /**
     * Shortcode: Chatbot completo
     */
    public function chatbot_shortcode($atts) {
        $atts = shortcode_atts(array(
            'theme' => 'light',
            'position' => 'bottom-right',
            'title' => 'Chatbot Inteligente',
            'welcome_message' => '¡Hola! ¿En qué puedo ayudarte?'
        ), $atts);
        
        ob_start();
        include CHATBOT_PLUGIN_PATH . 'templates/chatbot.php';
        return ob_get_clean();
    }
    
    /**
     * Shortcode: Widget del chatbot
     */
    public function chatbot_widget_shortcode($atts) {
        $atts = shortcode_atts(array(
            'theme' => 'light',
            'title' => 'Chatbot Widget'
        ), $atts);
        
        ob_start();
        include CHATBOT_PLUGIN_PATH . 'templates/widget.php';
        return ob_get_clean();
    }
    
    /**
     * Registrar widgets
     */
    public function register_widgets() {
        register_widget('ChatbotWidget');
    }
    
    /**
     * Menú de administración
     */
    public function admin_menu() {
        add_menu_page(
            'Chatbot Inteligente',
            'Chatbot',
            'manage_options',
            'chatbot-inteligente',
            array($this, 'admin_page'),
            'dashicons-format-chat',
            30
        );
        
        add_submenu_page(
            'chatbot-inteligente',
            'Configuración',
            'Configuración',
            'manage_options',
            'chatbot-config',
            array($this, 'config_page')
        );
        
        add_submenu_page(
            'chatbot-inteligente',
            'Estadísticas',
            'Estadísticas',
            'manage_options',
            'chatbot-stats',
            array($this, 'stats_page')
        );
    }
    
    /**
     * Página principal del admin
     */
    public function admin_page() {
        include CHATBOT_PLUGIN_PATH . 'templates/admin/dashboard.php';
    }
    
    /**
     * Página de configuración
     */
    public function config_page() {
        if (isset($_POST['submit'])) {
            update_option('chatbot_api_url', sanitize_url($_POST['api_url']));
            update_option('chatbot_openai_key', sanitize_text_field($_POST['openai_key']));
            update_option('chatbot_stripe_key', sanitize_text_field($_POST['stripe_key']));
            update_option('chatbot_paypal_client_id', sanitize_text_field($_POST['paypal_client_id']));
            update_option('chatbot_telegram_token', sanitize_text_field($_POST['telegram_token']));
            update_option('chatbot_facebook_token', sanitize_text_field($_POST['facebook_token']));
            update_option('chatbot_whatsapp_token', sanitize_text_field($_POST['whatsapp_token']));
            
            echo '<div class="notice notice-success"><p>Configuración guardada exitosamente.</p></div>';
        }
        
        include CHATBOT_PLUGIN_PATH . 'templates/admin/config.php';
    }
    
    /**
     * Página de estadísticas
     */
    public function stats_page() {
        include CHATBOT_PLUGIN_PATH . 'templates/admin/stats.php';
    }
    
    /**
     * Activación del plugin
     */
    public function activate() {
        // Crear tablas de base de datos si es necesario
        $this->create_tables();
        
        // Configuración por defecto
        add_option('chatbot_api_url', 'http://localhost:8000');
        add_option('chatbot_openai_key', '');
        add_option('chatbot_stripe_key', '');
        add_option('chatbot_paypal_client_id', '');
        add_option('chatbot_telegram_token', '');
        add_option('chatbot_facebook_token', '');
        add_option('chatbot_whatsapp_token', '');
        
        // Flush rewrite rules
        flush_rewrite_rules();
    }
    
    /**
     * Desactivación del plugin
     */
    public function deactivate() {
        flush_rewrite_rules();
    }
    
    /**
     * Crear tablas de base de datos
     */
    private function create_tables() {
        global $wpdb;
        
        $charset_collate = $wpdb->get_charset_collate();
        
        $sql = "CREATE TABLE IF NOT EXISTS {$wpdb->prefix}chatbot_conversations (
            id mediumint(9) NOT NULL AUTO_INCREMENT,
            user_id varchar(255) NOT NULL,
            session_id varchar(255) NOT NULL,
            platform varchar(50) DEFAULT 'web',
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            updated_at datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY user_id (user_id),
            KEY session_id (session_id)
        ) $charset_collate;
        
        CREATE TABLE IF NOT EXISTS {$wpdb->prefix}chatbot_messages (
            id mediumint(9) NOT NULL AUTO_INCREMENT,
            conversation_id mediumint(9) NOT NULL,
            content text NOT NULL,
            message_type varchar(50) DEFAULT 'text',
            sender varchar(50) DEFAULT 'user',
            metadata longtext,
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY conversation_id (conversation_id),
            FOREIGN KEY (conversation_id) REFERENCES {$wpdb->prefix}chatbot_conversations(id) ON DELETE CASCADE
        ) $charset_collate;
        
        CREATE TABLE IF NOT EXISTS {$wpdb->prefix}chatbot_appointments (
            id mediumint(9) NOT NULL AUTO_INCREMENT,
            user_id varchar(255) NOT NULL,
            service_type varchar(100) NOT NULL,
            appointment_date datetime NOT NULL,
            duration int DEFAULT 60,
            status varchar(50) DEFAULT 'pending',
            notes text,
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            updated_at datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY user_id (user_id),
            KEY status (status)
        ) $charset_collate;
        
        CREATE TABLE IF NOT EXISTS {$wpdb->prefix}chatbot_sales (
            id mediumint(9) NOT NULL AUTO_INCREMENT,
            user_id varchar(255) NOT NULL,
            product_id varchar(100) NOT NULL,
            quantity int DEFAULT 1,
            total_amount decimal(10,2) NOT NULL,
            status varchar(50) DEFAULT 'pending',
            payment_method varchar(50),
            payment_id varchar(255),
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            updated_at datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY user_id (user_id),
            KEY status (status)
        ) $charset_collate;";
        
        require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
        dbDelta($sql);
    }
}

/**
 * Widget del chatbot
 */
class ChatbotWidget extends WP_Widget {
    
    public function __construct() {
        parent::__construct(
            'chatbot_widget',
            'Chatbot Inteligente',
            array('description' => 'Widget del chatbot para la barra lateral')
        );
    }
    
    public function widget($args, $instance) {
        echo $args['before_widget'];
        
        if (!empty($instance['title'])) {
            echo $args['before_title'] . apply_filters('widget_title', $instance['title']) . $args['after_title'];
        }
        
        $theme = !empty($instance['theme']) ? $instance['theme'] : 'light';
        $welcome_message = !empty($instance['welcome_message']) ? $instance['welcome_message'] : '¡Hola! ¿En qué puedo ayudarte?';
        
        include CHATBOT_PLUGIN_PATH . 'templates/widget.php';
        
        echo $args['after_widget'];
    }
    
    public function form($instance) {
        $title = !empty($instance['title']) ? $instance['title'] : '';
        $theme = !empty($instance['theme']) ? $instance['theme'] : 'light';
        $welcome_message = !empty($instance['welcome_message']) ? $instance['welcome_message'] : '';
        
        ?>
        <p>
            <label for="<?php echo $this->get_field_id('title'); ?>">Título:</label>
            <input class="widefat" id="<?php echo $this->get_field_id('title'); ?>" name="<?php echo $this->get_field_name('title'); ?>" type="text" value="<?php echo esc_attr($title); ?>">
        </p>
        <p>
            <label for="<?php echo $this->get_field_id('theme'); ?>">Tema:</label>
            <select class="widefat" id="<?php echo $this->get_field_id('theme'); ?>" name="<?php echo $this->get_field_name('theme'); ?>">
                <option value="light" <?php selected($theme, 'light'); ?>>Claro</option>
                <option value="dark" <?php selected($theme, 'dark'); ?>>Oscuro</option>
            </select>
        </p>
        <p>
            <label for="<?php echo $this->get_field_id('welcome_message'); ?>">Mensaje de bienvenida:</label>
            <textarea class="widefat" id="<?php echo $this->get_field_id('welcome_message'); ?>" name="<?php echo $this->get_field_name('welcome_message'); ?>" rows="3"><?php echo esc_textarea($welcome_message); ?></textarea>
        </p>
        <?php
    }
    
    public function update($new_instance, $old_instance) {
        $instance = array();
        $instance['title'] = (!empty($new_instance['title'])) ? strip_tags($new_instance['title']) : '';
        $instance['theme'] = (!empty($new_instance['theme'])) ? strip_tags($new_instance['theme']) : 'light';
        $instance['welcome_message'] = (!empty($new_instance['welcome_message'])) ? strip_tags($new_instance['welcome_message']) : '';
        return $instance;
    }
}

// Inicializar plugin
new ChatbotInteligente();