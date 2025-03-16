// Function to toggle the dynamic configuration form based on deployment mode selection
function updateDynamicForm() {
    var modeSelect = document.getElementById('deployment-mode');
    var simpleConfig = document.getElementById('simple-config');
    var expertConfig = document.getElementById('expert-config');

    if (modeSelect.value === 'expert') {
        simpleConfig.style.display = 'none';
        expertConfig.style.display = 'block';
    } else {
        simpleConfig.style.display = 'block';
        expertConfig.style.display = 'none';
    }
}

// Existing functions
function showFeedback() {
    const action = document.querySelector('select[name="action"]').value;
    const feedback = document.getElementById('feedback');
    feedback.textContent = `You selected: ${action}`;
}

function toggleSubTree(event) {
    const subTree = event.target.nextElementSibling;
    if (subTree) {
        subTree.style.display = subTree.style.display === 'none' ? 'block' : 'none';
    }
}

function switchMode(mode) {
    document.getElementById('day-mode').disabled = mode !== 'day';
    document.getElementById('night-mode').disabled = mode !== 'night';
}

async function validateConfig() {
    const configInput = document.getElementById('config-input').value;
    const response = await fetch('/validate_config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ config: configInput })
    });
    const result = await response.json();
    const validationFeedback = document.getElementById('validation-feedback');
    if (result.valid) {
        validationFeedback.textContent = 'Configuration is valid.';
        validationFeedback.style.color = 'green';
    } else {
        validationFeedback.textContent = `Invalid configuration: ${result.error}`;
        validationFeedback.style.color = 'red';
    }
}

async function predictConfig() {
    const configInput = document.getElementById('config-input').value;
    const response = await fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ config: configInput })
    });
    const result = await response.json();
    const predictionFeedback = document.getElementById('prediction-feedback');
    if (result.prediction) {
        predictionFeedback.textContent = `Prediction: ${result.prediction}`;
        predictionFeedback.style.color = 'blue';
    } else {
        predictionFeedback.textContent = `Prediction error: ${result.error}`;
        predictionFeedback.style.color = 'red';
    }
}

// Function to toggle sidebars
function toggleSidebar(sidebarId) {
    var sidebar = document.getElementById(sidebarId);
    if (sidebar.style.display === 'none' || sidebar.style.display === '') {
        sidebar.style.display = 'block';
    } else {
        sidebar.style.display = 'none';
    }
}

function toggleStep(id) {
    var content = document.getElementById(id);
    if (content.style.display === 'none' || content.style.display === '') {
        content.style.display = 'block';
    } else {
        content.style.display = 'none';
    }
}

// Function to handle chat input
async function handleChatInput(event) {
    if (event.key === 'Enter') {
        const input = document.getElementById('chat-input').value;
        const chatWindow = document.getElementById('chat-window');
        chatWindow.innerHTML += `<div class='user-message'>${input}</div>`;
        document.getElementById('chat-input').value = '';
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: input })
        });
        const result = await response.json();
        chatWindow.innerHTML += `<div class='llm-response'>${result.response}</div>`;
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
}

// Function to show command suggestions
function showSuggestions() {
    const input = document.getElementById('command-input').value.toLowerCase();
    const suggestions = document.getElementById('suggestions');
    suggestions.innerHTML = '';
    if (input) {
        const filteredCommands = commands.filter(command => command.includes(input));
        filteredCommands.forEach(command => {
            const suggestionItem = document.createElement('div');
            suggestionItem.className = 'suggestion-item';
            suggestionItem.innerText = command;
            suggestionItem.onclick = () => {
                document.getElementById('command-input').value = command;
                suggestions.innerHTML = '';
            };
            suggestions.appendChild(suggestionItem);
        });
    }
}

// DeFi Oracle Meta Deployer - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
  // Initialize components
  initNavigation();
  initThemeToggle();
  initTooltips();
  initCards();
  initForms();
  handleResponsiveLayout();
  
  // Add event listeners for window resize
  window.addEventListener('resize', handleResponsiveLayout);
  
  // Form submission handler with real-time feedback
  const forms = document.querySelectorAll('form[data-remote="true"]');
  
  forms.forEach(form => {
      form.addEventListener('submit', async function(e) {
          e.preventDefault();
          const formData = new FormData(form);
          const submitButton = form.querySelector('button[type="submit"]');
          
          try {
              submitButton.disabled = true;
              submitButton.innerHTML = '<span class="spinner"></span> Processing...';
              
              const response = await fetch(form.action, {
                  method: form.method,
                  body: formData,
                  headers: {
                      'X-Requested-With': 'XMLHttpRequest'
                  }
              });
              
              const result = await response.json();
              
              if (!response.ok) throw new Error(result.error || 'Request failed');
              
              // Handle success
              if (form.dataset.successRedirect) {
                  window.location.href = form.dataset.successRedirect;
              }
              
          } catch (error) {
              console.error('Error:', error);
              const errorDiv = document.createElement('div');
              errorDiv.className = 'alert alert-danger';
              errorDiv.textContent = error.message;
              form.insertBefore(errorDiv, form.firstChild);
              removeElementAfterDelay(errorDiv, 5000);
          } finally {
              submitButton.disabled = false;
              submitButton.textContent = submitButton.dataset.originalText || 'Submit';
          }
      });
  });
  
  // Real-time validation
  const configInputs = document.querySelectorAll('[data-validate]');
  
  configInputs.forEach(input => {
      let debounceTimeout;
      
      input.addEventListener('input', function() {
          clearTimeout(debounceTimeout);
          debounceTimeout = setTimeout(async () => {
              try {
                  const response = await fetch('/validate_config', {
                      method: 'POST',
                      headers: {
                          'Content-Type': 'application/json',
                          'X-Requested-With': 'XMLHttpRequest'
                      },
                      body: JSON.stringify({ config: input.value })
                  });
                  
                  const result = await response.json();
                  
                  input.classList.remove('is-valid', 'is-invalid');
                  input.classList.add(result.valid ? 'is-valid' : 'is-invalid');
                  
                  const feedback = input.nextElementSibling;
                  if (feedback) {
                      feedback.textContent = result.valid ? 'Configuration is valid' : result.error;
                  }
                  
              } catch (error) {
                  console.error('Validation error:', error);
              }
          }, 500);
      });
  });

  initializeFormValidation();
  setupMonitoringToggle();
  initializeDocumentation();
  initializeFieldValidation();
});

/**
 * Initialize responsive navigation with mobile menu toggle
 */
function initNavigation() {
  const nav = document.querySelector('nav');
  if (!nav) return;
  
  // Add mobile menu toggle button if it doesn't exist
  if (!document.querySelector('.mobile-menu-toggle')) {
    const mobileMenuToggle = document.createElement('button');
    mobileMenuToggle.className = 'mobile-menu-toggle';
    mobileMenuToggle.setAttribute('aria-label', 'Toggle navigation menu');
    mobileMenuToggle.innerHTML = '<span></span><span></span><span></span>';
    
    nav.parentNode.insertBefore(mobileMenuToggle, nav);
    
    mobileMenuToggle.addEventListener('click', function() {
      nav.classList.toggle('active');
      mobileMenuToggle.classList.toggle('active');
      
      // Update aria-expanded attribute for accessibility
      const expanded = mobileMenuToggle.classList.contains('active');
      mobileMenuToggle.setAttribute('aria-expanded', expanded);
    });
  }
  
  // Add active class to current page link
  const currentPath = window.location.pathname;
  const navLinks = nav.querySelectorAll('a');
  
  navLinks.forEach(link => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
    
    // Add animation effect on hover
    link.addEventListener('mouseenter', function() {
      this.style.transition = 'all 0.3s ease';
    });
  });
}

/**
 * Theme toggle functionality (light/dark mode)
 */
function initThemeToggle() {
  // Create theme toggle button if it doesn't exist
  if (!document.querySelector('.theme-toggle')) {
    const themeToggle = document.createElement('button');
    themeToggle.className = 'theme-toggle';
    themeToggle.setAttribute('aria-label', 'Toggle dark/light mode');
    themeToggle.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><path d="M12 1v2M12 21v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M1 12h2M21 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4"></path></svg>';
    
    const header = document.querySelector('header');
    if (header) {
      header.appendChild(themeToggle);
    }
    
    // Get user preference from localStorage or system preference
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    const storedTheme = localStorage.getItem('theme');
    
    if (storedTheme === 'dark' || (!storedTheme && prefersDarkScheme.matches)) {
      document.body.classList.add('dark-theme');
      themeToggle.classList.add('active');
    } else {
      document.body.classList.remove('dark-theme');
    }
    
    // Add click event to toggle theme
    themeToggle.addEventListener('click', function() {
      document.body.classList.toggle('dark-theme');
      themeToggle.classList.toggle('active');
      
      const theme = document.body.classList.contains('dark-theme') ? 'dark' : 'light';
      localStorage.setItem('theme', theme);
    });
  }
}

/**
 * Initialize tooltip functionality
 */
function initTooltips() {
  const tooltips = document.querySelectorAll('[data-tooltip]');
  
  tooltips.forEach(tooltip => {
    tooltip.classList.add('tooltip');
    
    // For mobile/touch devices, add click event
    tooltip.addEventListener('click', function(e) {
      if (window.innerWidth < 768) {
        e.preventDefault();
        this.classList.toggle('tooltip-active');
      }
    });
  });
}

/**
 * Enhance card interactions
 */
function initCards() {
  const cards = document.querySelectorAll('.card');
  
  cards.forEach(card => {
    // Add hover interactions
    card.addEventListener('mouseenter', function() {
      this.style.transition = 'all 0.3s ease';
    });
    
    // If card has a button or link, make entire card clickable (optional)
    const cardLink = card.querySelector('a');
    const cardButton = card.querySelector('button');
    
    if (cardLink && !card.classList.contains('card-has-link')) {
      card.classList.add('card-has-link');
      card.style.cursor = 'pointer';
      
      card.addEventListener('click', function(e) {
        if (e.target !== cardLink && e.target.closest('a') !== cardLink) {
          cardLink.click();
        }
      });
    } else if (cardButton && !card.classList.contains('card-has-button')) {
      card.classList.add('card-has-button');
      card.style.cursor = 'pointer';
      
      card.addEventListener('click', function(e) {
        if (e.target !== cardButton && e.target.closest('button') !== cardButton) {
          cardButton.click();
        }
      });
    }
  });
}

/**
 * Form enhancements and validations
 */
function initForms() {
  const forms = document.querySelectorAll('form');
  
  forms.forEach(form => {
    // Add novalidate to use custom validation
    form.setAttribute('novalidate', '');
    
    // Add form validation
    form.addEventListener('submit', function(e) {
      if (!validateForm(this)) {
        e.preventDefault();
      }
    });
    
    // Add real-time validation on blur
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
      input.addEventListener('blur', function() {
        validateInput(this);
      });
      
      // Add floating label effect
      if (input.parentNode.classList.contains('form-group')) {
        input.addEventListener('focus', function() {
          this.parentNode.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
          if (!this.value) {
            this.parentNode.classList.remove('focused');
          }
        });
        
        // Set initial state for pre-filled inputs
        if (input.value) {
          input.parentNode.classList.add('focused');
        }
      }
    });
  });
}

/**
 * Validate form fields
 */
function validateForm(form) {
  let isValid = true;
  const inputs = form.querySelectorAll('input, select, textarea');
  
  inputs.forEach(input => {
    if (!validateInput(input)) {
      isValid = false;
    }
  });
  
  return isValid;
}

/**
 * Validate individual form field
 */
function validateInput(input) {
  const errorClass = 'has-error';
  let isValid = true;
  const errorMessage = input.dataset.errorMsg || 'Please fill out this field correctly.';
  
  // Remove any existing error message
  const existingError = input.nextElementSibling;
  if (existingError && existingError.classList.contains('error-message')) {
    existingError.remove();
  }
  
  // Check validity
  if (input.hasAttribute('required') && !input.value.trim()) {
    isValid = false;
  } else if (input.type === 'email' && input.value.trim() && !validateEmail(input.value)) {
    isValid = false;
  } else if (input.pattern && input.value.trim()) {
    const regex = new RegExp(input.pattern);
    if (!regex.test(input.value)) {
      isValid = false;
    }
  }
  
  // Show error message if invalid
  if (!isValid) {
    input.classList.add(errorClass);
    
    // Create error message element
    const errorSpan = document.createElement('span');
    errorSpan.className = 'error-message';
    errorSpan.textContent = errorMessage;
    
    // Insert error message after input
    input.parentNode.insertBefore(errorSpan, input.nextSibling);
    
  } else {
    input.classList.remove(errorClass);
  }
  
  return isValid;
}

/**
 * Validate email format
 */
function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

/**
 * Handle responsive layout adjustments
 */
function handleResponsiveLayout() {
  const isMobile = window.innerWidth < 768;
  const isTablet = window.innerWidth >= 768 && window.innerWidth < 1024;
  
  // Adjust navigation for mobile view
  const nav = document.querySelector('nav');
  if (nav) {
    nav.classList.toggle('mobile', isMobile);
    
    if (!isMobile && nav.classList.contains('active')) {
      nav.classList.remove('active');
      const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
      if (mobileMenuToggle) {
        mobileMenuToggle.classList.remove('active');
        mobileMenuToggle.setAttribute('aria-expanded', false);
      }
    }
  }
  
  // Add any other responsive layout changes here
  if (isMobile) {
    document.body.classList.add('is-mobile');
    document.body.classList.remove('is-tablet', 'is-desktop');
  } else if (isTablet) {
    document.body.classList.add('is-tablet');
    document.body.classList.remove('is-mobile', 'is-desktop');
  } else {
    document.body.classList.add('is-desktop');
    document.body.classList.remove('is-mobile', 'is-tablet');
  }
}

/**
 * Create animated notification
 */
function showNotification(message, type = 'info', duration = 3000) {
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.textContent = message;
  
  // Add to document
  document.body.appendChild(notification);
  
  // Trigger animation
  setTimeout(() => notification.classList.add('show'), 10);
  
  // Remove after duration
  setTimeout(() => {
    notification.classList.remove('show');
    notification.addEventListener('transitionend', function() {
      notification.remove();
    });
  }, duration);
  
  return notification;
}

// Initialize Socket.IO connection
const socket = io();

// Status update handler
socket.on('status_update', function(data) {
    const statusDiv = document.getElementById('status-updates') || createStatusDiv();
    const statusMessage = document.createElement('div');
    statusMessage.className = `alert alert-${data.status}`;
    statusMessage.textContent = data.message;
    statusDiv.appendChild(statusMessage);
    
    // Auto-remove success/error messages after 5 seconds
    if (data.status !== 'processing') {
        removeElementAfterDelay(statusMessage, 5000);
    }
});

function createStatusDiv() {
    const statusDiv = document.createElement('div');
    statusDiv.id = 'status-updates';
    statusDiv.className = 'status-container';
    document.body.insertBefore(statusDiv, document.body.firstChild);
    return statusDiv;
}

// Add CSS styles for status updates and animations
const style = document.createElement('style');
style.textContent = `
    .status-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        max-width: 300px;
    }
    
    .alert {
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 4px;
        animation: slideIn 0.3s ease-out;
    }
    
    .alert-success {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
    }
    
    .alert-error {
        background-color: #f8d7da;
        border-color: #f5c6cb;
        color: #721c24;
    }
    
    .alert-processing {
        background-color: #cce5ff;
        border-color: #b8daff;
        color: #004085;
    }
    
    .spinner {
        display: inline-block;
        width: 1em;
        height: 1em;
        border: 2px solid currentColor;
        border-right-color: transparent;
        border-radius: 50%;
        animation: spin 0.75s linear infinite;
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);

// Function to visualize the decision tree dynamically
function visualizeDecisionTree(treeData) {
    const treeContainer = document.getElementById('decision-tree-container');
    treeContainer.innerHTML = '';
    const tree = document.createElement('div');
    tree.className = 'decision-tree';
    buildTree(tree, treeData);
    treeContainer.appendChild(tree);
}

// Recursive function to build the tree structure
function buildTree(container, node) {
    const nodeElement = document.createElement('div');
    nodeElement.className = 'tree-node';
    nodeElement.textContent = node.name;
    container.appendChild(nodeElement);
    if (node.children) {
        const childrenContainer = document.createElement('div');
        childrenContainer.className = 'tree-children';
        node.children.forEach(child => buildTree(childrenContainer, child));
        container.appendChild(childrenContainer);
    }
}

// Function to handle real-time interaction with the decision tree
function handleTreeInteraction(event) {
    const targetNode = event.target;
    if (targetNode.classList.contains('tree-node')) {
        const nodeName = prompt('Enter new name for the node:', targetNode.textContent);
        if (nodeName) {
            targetNode.textContent = nodeName;
        }
    }
}

// Add event listener for tree interaction
document.getElementById('decision-tree-container').addEventListener('click', handleTreeInteraction);

// Example usage
const exampleTreeData = {
    name: 'Root',
    children: [
        { name: 'Child 1', children: [{ name: 'Grandchild 1' }, { name: 'Grandchild 2' }] },
        { name: 'Child 2' }
    ]
};
visualizeDecisionTree(exampleTreeData);

// Export functions for potential module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    initNavigation,
    initThemeToggle,
    initTooltips,
    initCards,
    initForms,
    handleResponsiveLayout,
    showNotification
  };
}

// Replace setTimeout with a function call
function removeElementAfterDelay(element, delay) {
  setTimeout(() => element.remove(), delay);
}

// Replace setInterval with a function call
function fetchRealtimeDataPeriodically(interval) {
  return setInterval(fetchRealtimeData, interval);
}

// Update the existing code to use the new functions
removeElementAfterDelay(errorDiv, 5000);
removeElementAfterDelay(statusMessage, 5000);
fetchRealtimeDataPeriodically(5000);

// Update other setTimeout usages
setTimeout(() => notification.classList.add('show'), 10);
setTimeout(() => {
  notification.classList.remove('show');
  notification.addEventListener('transitionend', function() {
    notification.remove();
  });
}, duration);

function initializeFormValidation() {
    const simpleForm = document.getElementById('simple-form');
    const expertForm = document.getElementById('expert-form');
    
    if (simpleForm) {
        simpleForm.addEventListener('submit', handleSimpleFormSubmit);
    }
    
    if (expertForm) {
        expertForm.addEventListener('submit', handleExpertFormSubmit);
    }

    // Add real-time validation on input change
    document.querySelectorAll('input, select').forEach(input => {
        input.addEventListener('change', () => validateField(input));
    });
}

function validateField(field) {
    const validityState = field.validity;
    const errorDiv = field.nextElementSibling;
    
    if (!validityState.valid) {
        let errorMessage = field.dataset.errorMsg || getDefaultErrorMessage(field, validityState);
        field.classList.add('is-invalid');
        if (errorDiv && errorDiv.classList.contains('invalid-feedback')) {
            errorDiv.textContent = errorMessage;
        }
        return false;
    } else {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        if (errorDiv && errorDiv.classList.contains('invalid-feedback')) {
            errorDiv.textContent = '';
        }
        return true;
    }
}

function getDefaultErrorMessage(field, validity) {
    if (validity.valueMissing) return 'This field is required';
    if (validity.typeMismatch) {
        switch(field.type) {
            case 'email': return 'Please enter a valid email address';
            case 'number': return 'Please enter a valid number';
            default: return 'Please enter a valid value';
        }
    }
    if (validity.patternMismatch) return field.dataset.errorMsg || 'Please match the requested format';
    if (validity.rangeUnderflow) return `Minimum value is ${field.min}`;
    if (validity.rangeOverflow) return `Maximum value is ${field.max}`;
    return 'Invalid value';
}

async function handleSimpleFormSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const isValid = validateForm(form);
    
    if (!isValid) {
        showNotification('Please fill in all required fields correctly', 'error');
        return;
    }

    const formData = {
        mode: 'simple',
        resourceGroup: document.getElementById('resource-group').value,
        location: document.getElementById('location').value,
        nodeType: document.getElementById('node-type').value,
        vmSize: document.getElementById('vm-size').value
    };

    await submitDeployment(formData);
}

async function handleExpertFormSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const isValid = validateForm(form);
    
    if (!isValid) {
        showNotification('Please fill in all required fields correctly', 'error');
        return;
    }

    const formData = {
        mode: 'expert',
        network: {
            vnetName: document.getElementById('vnet-name').value,
            subnetPrefix: document.getElementById('subnet-prefix').value
        },
        nodes: {
            count: document.getElementById('node-count').value,
            consensusProtocol: document.getElementById('consensus-protocol').value
        },
        monitoring: {
            enabled: document.getElementById('enable-monitoring').checked,
            retention: document.getElementById('metrics-retention').value,
            alertEmail: document.getElementById('alert-email').value
        }
    };

    await submitDeployment(formData);
}

async function submitDeployment(formData) {
    const deploymentStatus = document.getElementById('deployment-status');
    const progressBar = deploymentStatus.querySelector('.progress-bar');
    const statusMessage = document.getElementById('status-message');
    
    try {
        deploymentStatus.style.display = 'block';
        progressBar.style.width = '0%';
        statusMessage.textContent = 'Initializing deployment...';

        const response = await fetch('/deployer/deploy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error('Deployment failed');
        }

        const result = await response.json();
        
        // Update progress and status message based on deployment stages
        const deploymentStages = ['Validating', 'ResourceCreation', 'NodeDeployment', 'Configuration'];
        let currentStage = 0;

        const updateProgress = setInterval(() => {
            if (currentStage < deploymentStages.length) {
                const progress = (currentStage + 1) / deploymentStages.length * 100;
                progressBar.style.width = `${progress}%`;
                statusMessage.textContent = `${deploymentStages[currentStage]} in progress...`;
                currentStage++;
            } else {
                clearInterval(updateProgress);
                progressBar.style.width = '100%';
                statusMessage.textContent = 'Deployment completed successfully!';
                showNotification('Deployment completed successfully', 'success');
            }
        }, 2000);

    } catch (error) {
        progressBar.style.width = '100%';
        progressBar.classList.add('bg-danger');
        statusMessage.textContent = `Deployment failed: ${error.message}`;
        showNotification('Deployment failed: ' + error.message, 'error');
    }
}

function setupMonitoringToggle() {
    const monitoringCheckbox = document.getElementById('enable-monitoring');
    const monitoringOptions = document.getElementById('monitoring-options');
    
    if (monitoringCheckbox && monitoringOptions) {
        monitoringCheckbox.addEventListener('change', () => {
            monitoringOptions.style.display = monitoringCheckbox.checked ? 'block' : 'none';
            const inputs = monitoringOptions.querySelectorAll('input');
            inputs.forEach(input => {
                input.required = monitoringCheckbox.checked;
            });
        });
    }
}

function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.role = 'alert';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.querySelector('.status-container') || createStatusContainer();
    container.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, duration);
}

function createStatusContainer() {
    const container = document.createElement('div');
    container.className = 'status-container';
    document.body.appendChild(container);
    return container;
}

async function validateConfig(config, mode) {
    try {
        const response = await fetch(`/deployer/validate/${mode}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(config)
        });
        
        const result = await response.json();
        
        // Get feedback container or create one if it doesn't exist
        const feedbackContainer = document.getElementById('validation-feedback') || 
            createFeedbackContainer();
            
        feedbackContainer.innerHTML = ''; // Clear previous feedback
        
        if (result.valid) {
            feedbackContainer.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle"></i> Configuration is valid
                </div>`;
        } else {
            const errorList = result.errors.map(error => 
                `<li><i class="fas fa-exclamation-circle"></i> ${error}</li>`
            ).join('');
            
            feedbackContainer.innerHTML = `
                <div class="alert alert-danger">
                    <strong>Validation Errors:</strong>
                    <ul>${errorList}</ul>
                </div>`;
        }
        
        return result;
    } catch (error) {
        console.error('Validation error:', error);
        showNotification('Validation failed: ' + error.message, 'error');
        return { valid: false, errors: [error.message] };
    }
}

function createFeedbackContainer() {
    const container = document.createElement('div');
    container.id = 'validation-feedback';
    container.className = 'validation-feedback mt-3';
    
    const form = document.querySelector('form');
    form.appendChild(container);
    
    return container;
}

function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 
                             type === 'success' ? 'check-circle' : 
                             'info-circle'}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Auto dismiss
    if (duration > 0) {
        setTimeout(() => {
            notification.classList.remove('show');
            notification.addEventListener('transitionend', () => notification.remove());
        }, duration);
    }
}

// Initialize field validation on input/change
function initializeFieldValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        const mode = form.dataset.mode || 'simple';
        let debounceTimeout;
        
        inputs.forEach(input => {
            ['input', 'change'].forEach(eventType => {
                input.addEventListener(eventType, async () => {
                    clearTimeout(debounceTimeout);
                    debounceTimeout = setTimeout(async () => {
                        const formData = Object.fromEntries(new FormData(form));
                        const validationResult = await validateConfig(formData, mode);
                        
                        // Update field-specific feedback
                        if (!validationResult.valid) {
                            const fieldErrors = validationResult.errors.filter(
                                error => error.toLowerCase().includes(input.name.toLowerCase())
                            );
                            
                            if (fieldErrors.length > 0) {
                                input.classList.add('is-invalid');
                                input.classList.remove('is-valid');
                                
                                // Add or update error message
                                let errorDiv = input.nextElementSibling;
                                if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
                                    errorDiv = document.createElement('div');
                                    errorDiv.className = 'invalid-feedback';
                                    input.parentNode.insertBefore(errorDiv, input.nextSibling);
                                }
                                errorDiv.textContent = fieldErrors[0];
                            }
                        } else {
                            input.classList.remove('is-invalid');
                            input.classList.add('is-valid');
                            
                            // Remove error message if it exists
                            const errorDiv = input.nextElementSibling;
                            if (errorDiv && errorDiv.classList.contains('invalid-feedback')) {
                                errorDiv.remove();
                            }
                        }
                    }, 300); // Debounce delay
                });
            });
        });
    });
}

// Documentation features
function initializeDocumentation() {
    // Add syntax highlighting to code blocks
    if (typeof Prism !== 'undefined') {
        Prism.highlightAll();
    }

    // Add copy button to code blocks
    document.querySelectorAll('pre code').forEach(block => {
        const button = document.createElement('button');
        button.className = 'copy-button';
        button.textContent = 'Copy';
        button.addEventListener('click', () => {
            navigator.clipboard.writeText(block.textContent);
            button.textContent = 'Copied!';
            setTimeout(() => {
                button.textContent = 'Copy';
            }, 2000);
        });
        block.parentNode.appendChild(button);
    });

    // Add anchor links to headings
    document.querySelectorAll('.markdown-content h2, .markdown-content h3').forEach(heading => {
        const anchor = document.createElement('a');
        anchor.className = 'header-anchor';
        anchor.href = `#${heading.id}`;
        anchor.textContent = '#';
        heading.appendChild(anchor);
    });
}

// Initialize documentation features when the page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeFormValidation();
    setupMonitoringToggle();
    initializeDocumentation();
    initializeFieldValidation();
});