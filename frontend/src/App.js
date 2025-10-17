import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { FiSend, FiUser, FiMessageCircle, FiTruck, FiMapPin, FiMail } from 'react-icons/fi';
import axios from 'axios';

const AppContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
`;

const ChatContainer = styled.div`
  width: 100%;
  max-width: 800px;
  height: 80vh;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const ChatHeader = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  text-align: center;
  position: relative;
`;

const HeaderTitle = styled.h1`
  margin: 0;
  font-size: 24px;
  font-weight: 600;
`;

const HeaderSubtitle = styled.p`
  margin: 5px 0 0 0;
  opacity: 0.9;
  font-size: 14px;
`;

const ChatMessages = styled.div`
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

const Message = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 10px;
  ${props => props.isUser ? 'flex-direction: row-reverse;' : ''}
`;

const MessageAvatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${props => props.isUser ? '#667eea' : '#f0f0f0'};
  color: ${props => props.isUser ? 'white' : '#666'};
  flex-shrink: 0;
`;

const MessageContent = styled.div`
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 18px;
  background: ${props => props.isUser ? '#667eea' : '#f8f9fa'};
  color: ${props => props.isUser ? 'white' : '#333'};
  word-wrap: break-word;
  line-height: 1.4;
  
  ${props => props.isUser ? `
    border-bottom-right-radius: 4px;
  ` : `
    border-bottom-left-radius: 4px;
  `}
`;

const MessageTime = styled.div`
  font-size: 11px;
  opacity: 0.7;
  margin-top: 5px;
  text-align: ${props => props.isUser ? 'right' : 'left'};
`;

const ChatInput = styled.div`
  padding: 20px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 10px;
  align-items: center;
`;

const InputField = styled.input`
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 25px;
  outline: none;
  font-size: 14px;
  transition: border-color 0.3s ease;
  
  &:focus {
    border-color: #667eea;
  }
  
  &::placeholder {
    color: #999;
  }
`;

const SendButton = styled.button`
  width: 45px;
  height: 45px;
  border: none;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease;
  
  &:hover {
    transform: scale(1.05);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const LoadingDots = styled.div`
  display: flex;
  gap: 4px;
  align-items: center;
  
  span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #667eea;
    animation: bounce 1.4s ease-in-out infinite both;
    
    &:nth-child(1) { animation-delay: -0.32s; }
    &:nth-child(2) { animation-delay: -0.16s; }
    &:nth-child(3) { animation-delay: 0s; }
  }
  
  @keyframes bounce {
    0%, 80%, 100% {
      transform: scale(0);
    }
    40% {
      transform: scale(1);
    }
  }
`;

const QuickActions = styled.div`
  display: flex;
  gap: 10px;
  margin-top: 10px;
  flex-wrap: wrap;
`;

const QuickActionButton = styled.button`
  padding: 8px 16px;
  border: 1px solid #667eea;
  border-radius: 20px;
  background: white;
  color: #667eea;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s ease;
  
  &:hover {
    background: #667eea;
    color: white;
  }
`;

const CarComparison = styled.div`
  background: #f8f9fa;
  border-radius: 12px;
  padding: 15px;
  margin: 10px 0;
  border-left: 4px solid #667eea;
`;

const ShowroomCard = styled.div`
  background: #f8f9fa;
  border-radius: 12px;
  padding: 15px;
  margin: 10px 0;
  border-left: 4px solid #28a745;
`;

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Xin chào! Tôi là AI agent tư vấn bán xe. Tôi có thể giúp bạn:\n• Tìm xe phù hợp với ngân sách và nhu cầu\n• So sánh các mẫu xe\n• Tìm showroom gần nhất\n• Đăng ký lái thử\n\nBạn có thể cho tôi biết ngân sách và yêu cầu của bạn không?",
      isUser: false,
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [userContext, setUserContext] = useState({});
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: inputValue,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await axios.post('/api/chat', {
        message: inputValue,
        context: userContext
      });

      const botMessage = {
        id: Date.now() + 1,
        text: response.data.response,
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.",
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const quickActions = [
    "Tôi muốn mua xe dưới 1 tỷ",
    "Tôi cần xe 7 chỗ",
    "Tôi muốn xe SUV",
    "Tôi cần xe tiết kiệm nhiên liệu"
  ];

  const handleQuickAction = (action) => {
    setInputValue(action);
  };

  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString('vi-VN', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const renderMessage = (message) => {
    const isUser = message.isUser;
    
    return (
      <Message key={message.id} isUser={isUser}>
        <MessageAvatar isUser={isUser}>
          {isUser ? <FiUser size={20} /> : <FiMessageCircle size={20} />}
        </MessageAvatar>
        <div style={{ maxWidth: '70%' }}>
          <MessageContent isUser={isUser}>
            {message.text.split('\n').map((line, index) => (
              <div key={index}>
                {line}
                {index < message.text.split('\n').length - 1 && <br />}
              </div>
            ))}
          </MessageContent>
          <MessageTime isUser={isUser}>
            {formatTime(message.timestamp)}
          </MessageTime>
        </div>
      </Message>
    );
  };

  return (
    <AppContainer>
      <ChatContainer>
        <ChatHeader>
          <HeaderTitle>
            <FiTruck style={{ marginRight: '10px', verticalAlign: 'middle' }} />
            AI Car Agent
          </HeaderTitle>
          <HeaderSubtitle>
            Tư vấn mua xe thông minh - Tìm xe phù hợp với bạn
          </HeaderSubtitle>
        </ChatHeader>

        <ChatMessages>
          {messages.map(renderMessage)}
          
          {isLoading && (
            <Message>
              <MessageAvatar>
                <FiMessageCircle size={20} />
              </MessageAvatar>
              <MessageContent>
                <LoadingDots>
                  <span></span>
                  <span></span>
                  <span></span>
                </LoadingDots>
              </MessageContent>
            </Message>
          )}
          
          {messages.length === 1 && (
            <QuickActions>
              {quickActions.map((action, index) => (
                <QuickActionButton
                  key={index}
                  onClick={() => handleQuickAction(action)}
                >
                  {action}
                </QuickActionButton>
              ))}
            </QuickActions>
          )}
          
          <div ref={messagesEndRef} />
        </ChatMessages>

        <ChatInput>
          <InputField
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Nhập tin nhắn của bạn..."
            disabled={isLoading}
          />
          <SendButton onClick={sendMessage} disabled={isLoading || !inputValue.trim()}>
            <FiSend size={20} />
          </SendButton>
        </ChatInput>
      </ChatContainer>
    </AppContainer>
  );
}

export default App;
