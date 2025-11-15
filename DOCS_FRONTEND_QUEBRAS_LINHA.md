# Exibição de Quebras de Linha no Frontend React

## 🔍 Problema

O backend FastAPI retorna a resposta com quebras de linha (`\n`), mas o **navegador não renderiza `\n` automaticamente** em HTML - ele trata como espaço.

**Exemplo:**
```javascript
// Backend retorna:
"Plano Essencial:\nR$ 260/mês\nBenefícios:\n• Item 1"

// Navegador exibe:
"Plano Essencial: R$ 260/mês Benefícios: • Item 1"
```

## ✅ Soluções para React

### Solução 1: CSS `white-space: pre-line` (RECOMENDADO)

No componente React que exibe a mensagem do bot:

```jsx
// MessageBubble.jsx ou similar
const MessageBubble = ({ message }) => {
  return (
    <div 
      className="bot-message"
      style={{ whiteSpace: 'pre-line' }}
    >
      {message}
    </div>
  );
};
```

**Ou no CSS:**
```css
/* styles.css */
.bot-message {
  white-space: pre-line;
  /* Preserva quebras de linha (\n) mas colapsa espaços múltiplos */
}

/* Alternativa: preservar tudo */
.bot-message-exact {
  white-space: pre-wrap;
  /* Preserva quebras E espaços múltiplos */
}
```

### Solução 2: Converter `\n` para `<br>` (Manual)

```jsx
const MessageBubble = ({ message }) => {
  // Converter \n em <br> tags
  const formatMessage = (text) => {
    return text.split('\n').map((line, index) => (
      <React.Fragment key={index}>
        {line}
        {index < text.split('\n').length - 1 && <br />}
      </React.Fragment>
    ));
  };

  return (
    <div className="bot-message">
      {formatMessage(message)}
    </div>
  );
};
```

### Solução 3: Usar `dangerouslySetInnerHTML` (CUIDADO)

```jsx
const MessageBubble = ({ message }) => {
  // Sanitizar primeiro para evitar XSS
  const formatMessage = (text) => {
    return text.replace(/\n/g, '<br>');
  };

  return (
    <div 
      className="bot-message"
      dangerouslySetInnerHTML={{ __html: formatMessage(message) }}
    />
  );
};

// ⚠️ ATENÇÃO: Use com cuidado! Pode causar XSS se o conteúdo não for confiável
```

### Solução 4: Biblioteca `react-markdown` (Se quiser suporte Markdown)

```bash
npm install react-markdown
```

```jsx
import ReactMarkdown from 'react-markdown';

const MessageBubble = ({ message }) => {
  return (
    <div className="bot-message">
      <ReactMarkdown>{message}</ReactMarkdown>
    </div>
  );
};
```

## 🎨 Exemplo Completo

### Componente de Chat

```jsx
// ChatMessage.jsx
import React from 'react';
import './ChatMessage.css';

const ChatMessage = ({ message, isBot }) => {
  return (
    <div className={`message ${isBot ? 'bot' : 'user'}`}>
      <div className="message-bubble">
        {message}
      </div>
    </div>
  );
};

export default ChatMessage;
```

### CSS

```css
/* ChatMessage.css */
.message {
  display: flex;
  margin: 10px 0;
}

.message.user {
  justify-content: flex-end;
}

.message.bot {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  
  /* 🔑 IMPORTANTE: Preservar quebras de linha */
  white-space: pre-line;
  word-wrap: break-word;
}

.message.user .message-bubble {
  background-color: #007bff;
  color: white;
}

.message.bot .message-bubble {
  background-color: #f1f3f4;
  color: #202124;
}

/* Suporte para negrito (*texto*) se quiser */
.message-bubble strong {
  font-weight: 600;
}
```

### Componente de Chat Completo

```jsx
// SimulationChat.jsx
import React, { useState } from 'react';
import ChatMessage from './ChatMessage';

const SimulationChat = ({ userId }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Adicionar mensagem do usuário
    const userMessage = { text: input, isBot: false };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Chamar API
      const response = await fetch('http://localhost:8000/simulation/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          message: input
        })
      });

      const data = await response.json();

      // Adicionar resposta do bot
      const botMessage = { 
        text: data.reply,  // ✅ Já vem com \n
        isBot: true 
      };
      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error('Erro:', error);
      const errorMessage = { 
        text: 'Desculpe, ocorreu um erro.', 
        isBot: true 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, index) => (
          <ChatMessage 
            key={index}
            message={msg.text}
            isBot={msg.isBot}
          />
        ))}
        {loading && <ChatMessage message="Digitando..." isBot={true} />}
      </div>
      
      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Digite sua mensagem..."
        />
        <button onClick={sendMessage}>Enviar</button>
      </div>
    </div>
  );
};

export default SimulationChat;
```

## 🎯 Solução Mais Simples

**Se você já tem um componente que exibe as mensagens**, adicione apenas:

```jsx
// Antes
<div className="bot-message">
  {message}
</div>

// Depois - adicione style
<div 
  className="bot-message"
  style={{ whiteSpace: 'pre-line' }}
>
  {message}
</div>
```

**Ou no CSS global:**
```css
.bot-message,
.assistant-message,
.ai-response {
  white-space: pre-line;
}
```

## 🧪 Teste Rápido

No console do navegador (DevTools):

```javascript
// Testar se white-space funciona
const div = document.querySelector('.bot-message');
div.style.whiteSpace = 'pre-line';

// Deve mostrar quebras de linha agora
```

## 📋 Checklist

- [ ] Componente de mensagem do bot tem `white-space: pre-line`
- [ ] CSS está sendo aplicado corretamente
- [ ] Mensagem está sendo passada como string (não HTML)
- [ ] Não há `.trim()` ou `.replace('\n', ' ')` no código

## 🔍 Debug

Se ainda não funcionar:

```jsx
// Adicione console.log para ver a resposta
const data = await response.json();
console.log('Resposta bruta:', data.reply);
console.log('Tem \\n?', data.reply.includes('\n'));
console.log('Número de \\n:', (data.reply.match(/\n/g) || []).length);
```

## ✅ Resultado Esperado

**Antes (sem white-space):**
```
Plano Essencial: R$ 260/mês O que está incluído: • Item 1 • Item 2
```

**Depois (com white-space: pre-line):**
```
Plano Essencial:
R$ 260/mês

O que está incluído:
• Item 1
• Item 2
```

## 🎨 Suporte a Markdown Básico (Opcional)

Se quiser converter os `*texto*` em negrito:

```jsx
const formatMessage = (text) => {
  // Converter *texto* em <strong>texto</strong>
  return text.replace(/\*(.*?)\*/g, '<strong>$1</strong>');
};

<div 
  className="bot-message"
  style={{ whiteSpace: 'pre-line' }}
  dangerouslySetInnerHTML={{ __html: formatMessage(message) }}
/>
```

## 📚 Referências

- [MDN: white-space](https://developer.mozilla.org/en-US/docs/Web/CSS/white-space)
- [React: Displaying Text with Line Breaks](https://react.dev/learn#displaying-lists)
- [react-markdown](https://github.com/remarkjs/react-markdown)
