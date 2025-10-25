import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { FiSend, FiUser, FiMessageCircle, FiTruck, FiSmile, FiFrown } from 'react-icons/fi';
import axios from 'axios';
import { Volume2, VolumeOff } from "lucide-react"


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
  .row-inline-between{
  display:inline-flex;
  align-items: center;
  justify-content: space-between;
  gap:20px;
  }
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
  width: 100%;
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

// const CarComparison = styled.div`
//   background: #f8f9fa;
//   border-radius: 12px;
//   padding: 15px;
//   margin: 10px 0;
//   border-left: 4px solid #667eea;
// `;

// const ShowroomCard = styled.div`
//   background: #f8f9fa;
//   border-radius: 12px;
//   padding: 15px;
//   margin: 10px 0;
//   border-left: 4px solid #28a745;
// `;

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Xin chào! Tôi là AI agent tư vấn bán xe. Tôi có thể giúp bạn:\n• Tìm xe phù hợp với ngân sách và nhu cầu\n• So sánh các mẫu xe\n• Tìm showroom gần nhất\n• Đăng ký lái thử\n\nBạn có thể cho tôi biết ngân sách và yêu cầu của bạn không?",
      isUser: false,
      timestamp: new Date()
    }
  ]);
  const [isPlay, setPlay] = useState(false)
  const [src, setSrc] = useState(null)
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  const setPayloadToSendMessage = (inputValue) => {
    let payLoad = {};
    if (inputValue.length !== 0) {
      let lowerInputValue = inputValue.toLowerCase();
      let indexFindImage = lowerInputValue.includes("ảnh") || lowerInputValue.includes("hình ảnh") || lowerInputValue.includes("image") || lowerInputValue.includes("photo");
      if(indexFindImage){
        payLoad.isFunctionCall = true;
      }

      let indexDatabaseQuery = lowerInputValue.includes("gợi ý") || lowerInputValue.includes("đề xuất") || lowerInputValue.includes("tư vấn") || lowerInputValue.includes("recommendation");
      if(indexDatabaseQuery){
        payLoad.isDatabaseQuery = true;
      }


    }
    let lastFewMessages = messages.map(item => {
      return {
        "role": item.isUser ? "user" : "assistant",
        "content": item.text
      }
    }
    );
    let idx = 1;
    while (idx < lastFewMessages.length) {
      const x = lastFewMessages[idx]
      let rejectContent = x.content.toLowerCase();
      let indexRejectContent = rejectContent.indexOf("xin lỗi") || rejectContent.indexOf("đặt lại câu hỏi") || rejectContent.indexOf("ngoài phạm vi");

      if (x.content && indexRejectContent !== -1) {
        lastFewMessages.splice(idx - 1, 2);
      } else idx++
    }
    lastFewMessages.push({ "role": "user", "content": inputValue })
    const roleSystem = {
      "role": "system", "content": `Bạn là một chuyên gia sale trong lĩnh vực mua bán xe hơi tại thị trường Việt Nam.
        Nếu như câu hỏi là những thứ ngoài lĩnh vực này thì hãy trả lời là:
        Xin lỗi bạn đây là câu hỏi nằm ngoài lĩnh vực của tôi. Xin hãy đặt lại câu hỏi.`}
    // lastFewMessages.unshift(roleSystem);
    payLoad.promptMessageList = lastFewMessages.slice(-10);
    payLoad.promptMessageList.unshift(roleSystem);
    return payLoad;
  }
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
    const payload = setPayloadToSendMessage(inputValue);
    try {
      const response = await axios.post('/api/chat', payload);

      const botMessage = {
        id: response.data.response?.id || Date.now() + 1,
        text: response.data.response?.message || "",
        images: response.data.images,
        isUser: false,
        timestamp: new Date(),
        audioId: response.data.response?.id
      };
      response.data.response?.message && handlePlayAudio(botMessage.audioId)
      setMessages(prev => [...prev, botMessage]);
      console.log("messages", messages)
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
    "Tôi cần xe tiết kiệm nhiên liệu",
    "Tôi muốn tìm ảnh chi tiết về xe "
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

  const handlePlayAudio = async (id = "333") => {
    if (isPlay) {
      handleOffPlayAudio()
      return
    }
    try {
      setPlay(true);
      const response = await axios.post('/api/getaudio', { id }, { responseType: "arraybuffer" });
      const buf = await response?.data || [];
      const ctx = new AudioContext();
      const audio = await ctx.decodeAudioData(buf);
      const src = ctx.createBufferSource();
      src.buffer = audio;
      src.connect(ctx.destination);
      src.start(0);
      setSrc(src)
    } catch (_) {
      //
    }
  }

  const handleOffPlayAudio = () => {
    src?.stop?.();
    setPlay(false)
  }

  const renderMessage = (message) => {
    const isUser = message.isUser;

    return (
      <Message key={message.id} isUser={isUser}>
        <MessageAvatar isUser={isUser}>
          {isUser ? <FiUser size={20} /> : <FiMessageCircle size={20} />}
        </MessageAvatar>
        <div style={{ maxWidth: '70%' }}>
          <MessageContent isUser={isUser} className='message-content'>
            {message.text?.split('\n').map((line, index) => (
              <div key={index} style={{ width: '100%' }}>
                {line}
                {index < message.text.split('\n').length - 1 && <br />}
              </div>
            ))}
            {message.images ? <img src={message.images} alt="car" style={{ maxWidth: '100%', marginTop: '10px', borderRadius: '8px' }} /> : null}
          </MessageContent>
          <div className="row-inline-between w-100" style={{ width: '100%', marginTop: '20px' }}>
            <MessageTime isUser={isUser}>
              {formatTime(message.timestamp)} {(!isUser && message.id > 1) ? <> <FiSmile size={18} style={{ marginLeft: "5px" }} /> <span style={{ marginRight: "5px" }}></span> <FiFrown size={18} /></> : null}
            </MessageTime>
            {message.audioId && (isPlay ?
              <Volume2 size={"20px"} onClick={() => handlePlayAudio(message?.audioId)} />
              : <VolumeOff size={"20px"} onClick={() => handlePlayAudio(message?.audioId)} />)}
          </div>

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
      <audio style={{ visibility: "hidden" }} id="player" controls></audio>
    </AppContainer>
  );
}

export default App;
