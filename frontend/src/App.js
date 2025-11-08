import { useState, useEffect, useRef } from "react";
import styled from "styled-components";
import {
  FiSend,
  FiUser,
  FiTruck,
  FiThumbsUp,
  FiThumbsDown,
  FiCopy,
  FiVolume2,
  FiVolumeX,
  FiMic
} from "react-icons/fi";
import { RiChatNewLine } from "react-icons/ri";
import axios from "axios";
import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

const AppContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  position: relative;
  .new-chat{
    position: absolute;
    top: 24px;
    right: 30px;
    font-size: 20px;
    cursor: pointer;
  }
  .MIC{
    display: inline-flex;
    cursor: pointer;
    align-items: center;
    justify-content: center;
    width: 30px;
    height: 30px;
    background: #ccc;
    border-radius: 50%;
    &.active {
      background: #64f897;
    }
  }
`;

const ChatContainer = styled.div`
  width: 100%;
  max-width: 800px;
  min-height: 600px;
  margin: auto auto;
  height: 90vh;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  @media (max-width: 600px) {
  border-radius: 0px;
  }
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
  .row-inline-between {
    opacity: 0.6;
    display: inline-flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
  }
`;

const Message = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 10px;
  ${(props) => (props.isUser ? "flex-direction: row-reverse;" : "")}
`;

const MessageAvatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${(props) => (props.isUser ? "#667eea" : "#f0f0f0")};
  color: ${(props) => (props.isUser ? "white" : "#666")};
  flex-shrink: 0;
`;

const MessageContent = styled.div`
  width: 100%;
  padding: 12px 16px;
  border-radius: 18px;
  background: ${(props) => (props.isUser ? "#667eea" : "#f8f9fa")};
  color: ${(props) => (props.isUser ? "white" : "#333")};
  word-wrap: break-word;
  line-height: 1.4;
  ol { margin-left: 30px }

  ${(props) =>
    props.isUser
      ? `
    border-bottom-right-radius: 4px;
  `
      : `
    border-bottom-left-radius: 4px;
  `}
`;

const MessageTime = styled.div`
  font-size: 11px;
  text-align: ${(props) => (props.isUser ? "right" : "left")};
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

    &:nth-child(1) {
      animation-delay: -0.32s;
    }
    &:nth-child(2) {
      animation-delay: -0.16s;
    }
    &:nth-child(3) {
      animation-delay: 0s;
    }
  }

  @keyframes bounce {
    0%,
    80%,
    100% {
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

const TypewriterEffect = ({
  processedText,
  typingSpeed = 10,
  onRenderingEnd,
}) => {
  const [visibleLength, setVisibleLength] = useState(0);
  const contentRef = useRef(null);
  useEffect(() => {
    if (visibleLength < processedText.length) {
      const timer = setTimeout(() => {
        let step = 1;
        if (processedText.charAt(visibleLength) === '|') { // skip each row in table
          const nextIdxOf = processedText.indexOf("|\n", visibleLength)
          step = nextIdxOf - visibleLength + 1;
        } else if (processedText.charAt(visibleLength) === '(') { // skip image url
          const nextIdxOf = processedText.indexOf(")", visibleLength) || processedText.indexOf("\n", visibleLength)
          step = nextIdxOf - visibleLength + 1;
        }
        if (step < 1) step = 1;
        setVisibleLength(visibleLength + step);
        if (step > 1 || visibleLength % 100 === 0)
          scrollChatView();
      }, typingSpeed);
      return () => clearTimeout(timer);
    } else if (onRenderingEnd) {
      onRenderingEnd();
      scrollChatView();
    }
  });
  return (
    <div ref={contentRef}>
      <CustomReactMarkdown content={processedText.substring(0, visibleLength)} />
      {visibleLength < processedText.length && <span className="typing-indicator" />}
    </div>
  );
};

const CustomReactMarkdown = ({ content, className }) => (
  <Markdown
    remarkPlugins={[remarkGfm]}
    components={{
      // Custom renderers for table elements
      th: ({ node, ...props }) => <th className="th" {...props} />,
      td: ({ node, ...props }) => <td className="td" {...props} />,
      // Add other custom renderers as needed
    }}
  >
    {content}
  </Markdown>
);

const scrollChatView = () => {
  const messagesEndRef = document.getElementById("messagesEndRef");
  messagesEndRef?.scrollIntoView({ behavior: "smooth" });
}

function App() {
  const startMessage = [
    {
      id: 1,
      text: "Xin chào! Tôi là AI agent tư vấn bán xe. Tôi có thể giúp bạn:\n\n• Tìm xe phù hợp với ngân sách và nhu cầu\n\n• So sánh các mẫu xe\n\n• Tìm showroom gần nhất\n\n• Đăng ký lái thử\n\nBạn có thể cho tôi biết ngân sách và yêu cầu của bạn không?",
      isUser: false,
      timestamp: new Date(),
    },
  ]
  const [messages, setMessages] = useState([...startMessage]);
  const [isPlay, setPlay] = useState(false);
  const [src, setSrc] = useState(null);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingAudio, setIsLoadingAudio] = useState(false);
  const messagesEndRef = useRef(null);
  const [useMic, setMic] = useState(false)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);


  useEffect(() => {
    const handleClick = (e) => {
      const link = e.target.closest("a");
      if (link && link.tagName === "A" && link.href) {
        e.preventDefault();
        window.open(link.href, "_blank");
      }
    };

    document.addEventListener("click", handleClick);
    return () => document.removeEventListener("click", handleClick);
  }, []);

  const setPayloadToSendMessage = (inputValue) => {
    const payLoad = {};

    if (inputValue.length !== 0) {
      const lowerInputValue = inputValue.toLowerCase();
      const indexFindImage =
        lowerInputValue.includes("tìm ảnh") ||
        lowerInputValue.includes("tìm hình ảnh") ||
        lowerInputValue.includes("image") ||
        lowerInputValue.includes("photo");
      if (indexFindImage)
        payLoad.isFunctionCall = true;

      const indexDatabaseQuery =
        lowerInputValue.includes("tư vấn") ||
        lowerInputValue.includes("đề xuất")
      if (indexDatabaseQuery)
        payLoad.isDatabaseQuery = true;

      const indexSimilarCarQuery =
        lowerInputValue.includes("gợi ý") ||
        lowerInputValue.includes("tương tự") ||
        lowerInputValue.includes("recommend");
      if (indexSimilarCarQuery)
        payLoad.isSimilarCarQuery = true;

      const indexLangchainSearch =
        lowerInputValue.includes("tìm kiếm")
      if (indexLangchainSearch)
        payLoad.isLangchainSearch = true;

      if (lowerInputValue.includes("so sánh"))
        inputValue += " trả lời dưới dạng bảng ví dụ như sau | Header 1 | Header 2 | Header 3 | | :------- | :------: | -------: | | Row 1 Col 1 | Row 1 Col 2 | Row 1 Col 3 | | Row 2 Col 1 | Row 2 Col 2 | Row 2 Col 3 |"
    }
    const lastFewMessages = messages.map((item) => {
      return {
        role: item.isUser ? "user" : "assistant",
        content: item.text,
      };
    });
    let idx = 1;
    while (idx < lastFewMessages.length) {
      const x = lastFewMessages[idx];
      const rejectContent = x.content.toLowerCase();
      const indexRejectContent =
        rejectContent.indexOf("xin lỗi") ??
        rejectContent.indexOf("đặt lại câu hỏi") ??
        rejectContent.indexOf("ngoài phạm vi");

      if (x.content && indexRejectContent !== -1) {
        lastFewMessages.splice(idx - 1, 2);
      } else idx++;
    }
    lastFewMessages.push({ role: "user", content: inputValue });
    const roleSystem = {
      role: "system",
      content: `Bạn là một chuyên gia sale trong lĩnh vực mua bán xe hơi tại thị trường Việt Nam.
        Nếu như câu hỏi là những thứ ngoài lĩnh vực này thì hãy trả lời là:
        Xin lỗi bạn đây là câu hỏi nằm ngoài lĩnh vực của tôi. Xin hãy đặt lại câu hỏi.`,
    };
    // lastFewMessages.unshift(roleSystem);
    payLoad.promptMessageList = lastFewMessages.slice(-10);
    payLoad.promptMessageList.unshift(roleSystem);
    return payLoad;
  };
  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;
    const userMessage = {
      id: Date.now(),
      text: inputValue,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);
    const payload = setPayloadToSendMessage(inputValue);
    try {
      const response = await axios.post("/api/chat", payload);

      const botMessage = {
        id: response.data.response?.id || Date.now() + 1,
        text: response.data.response?.message || "",
        images: response.data.images,
        isUser: false,
        timestamp: new Date(),
        audioId: response.data.response?.id,
      };
      // response.data.response?.message &&
      //   handlePlayAudio(botMessage.audioId, true);
      setMessages((prev) => [...prev, botMessage]);
      console.log("messages", messages);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage = {
        id: Date.now() + 1,
        text: "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.",
        isUser: false,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const quickActions = [
    "Tôi muốn mua xe dưới 1 tỷ",
    "Tôi cần xe 7 chỗ",
    "Tôi muốn xe SUV",
    "Tôi cần xe tiết kiệm nhiên liệu",
    "Tôi muốn tìm ảnh chi tiết về xe ",
  ];

  const handleQuickAction = (action) => {
    setInputValue(action);
  };

  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString("vi-VN", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const handleNewChat = async () => {
    setMessages([...startMessage]);
  }

  const handlePlayAudio = async (id, text, force) => {
    handleOffPlayAudio();
    if (isPlay && !force) {
      return;
    }
    try {
      setPlay(true);
      setIsLoadingAudio(true);
      const response = await axios.post(
        "/api/getaudio",
        { id, text },
        { responseType: "arraybuffer" },
      );
      const buf = (await response?.data) || [];
      const ctx = new AudioContext();
      const audio = await ctx.decodeAudioData(buf);
      const src = ctx.createBufferSource();
      src.buffer = audio;
      src.connect(ctx.destination);
      src.start(0);
      setSrc(src);
      setTimeout(() => {
        setIsLoadingAudio(false);
      }, 750);
    } catch (_) {
      //
    }
  };

  const handleOffPlayAudio = () => {
    src?.stop?.();
    setPlay(false);
  };

  const handleMIC = () => {
    setMic(pre => !pre);
    setInputValue("")
  }

  const renderMessage = (message) => {
    const isUser = message.isUser;

    return (
      <Message key={message.id} isUser={isUser}>
        <MessageAvatar isUser={isUser}>
          {isUser ? <FiUser size={20} /> : <FiTruck size={20} />}
        </MessageAvatar>
        <div style={{ maxWidth: "70%" }}>
          <MessageContent isUser={isUser} className="message-content">
            {isUser ? <Markdown remarkPlugins={[remarkGfm]}>
              {message.text}
            </Markdown> :
              <TypewriterEffect processedText={message.text} onRenderingEnd={() => { }} />}
            {message.images ? (
              <img
                src={message.images}
                alt="car"
                style={{
                  maxWidth: "100%",
                  marginTop: "10px",
                  borderRadius: "8px",
                }}
              />
            ) : null}
          </MessageContent>
          <div
            className="row-inline-between w-100"
            style={{ width: "100%" }}
          >
            <MessageTime isUser={isUser}>
              {formatTime(message.timestamp)}{" "}
              {!isUser && message.id !== 1 ? (
                <>
                  {" "}
                  <FiThumbsUp size={18} style={{ marginLeft: "10px", cursor: "pointer" }} />{" "}
                  <FiThumbsDown size={18} style={{ marginLeft: "7px", cursor: "pointer" }} />
                  <FiCopy size={18} style={{ marginLeft: "11px", cursor: "pointer" }} />
                </>
              ) : null}
            </MessageTime>
            {message.audioId && message.text &&
              (isLoadingAudio ?
                <LoadingDots>
                  <span></span>
                  <span></span>
                  <span></span>
                </LoadingDots> :
                isPlay ? (
                  <FiVolumeX
                    size={18}
                    style={{ cursor: "pointer" }}
                    onClick={() => handlePlayAudio(message?.audioId, message.text)}
                  />
                ) : (
                  <FiVolume2
                    size={18}
                    style={{ cursor: "pointer" }}
                    onClick={() => handlePlayAudio(message?.audioId, message.text)}
                  />
                ))}
          </div>
        </div>
      </Message>
    );
  };

  return (
    <AppContainer>
      <ChatContainer className="ChatContainer">
        <ChatHeader>
          <div>
            <HeaderTitle>
              <FiTruck style={{ marginRight: "10px", verticalAlign: "middle" }} />
              AI Car Agent
            </HeaderTitle>
            <HeaderSubtitle>
              Tư vấn mua xe thông minh - Tìm xe phù hợp với bạn
            </HeaderSubtitle>
          </div>
          <div className="new-chat">
            <RiChatNewLine onClick={handleNewChat} />
          </div>
        </ChatHeader>

        <ChatMessages>
          {messages.map(renderMessage)}

          {isLoading && (
            <Message>
              <MessageAvatar>
                <FiTruck size={20} />
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

          <div id="messagesEndRef" ref={messagesEndRef} />
        </ChatMessages>

        <ChatInput>
          <div onClick={handleMIC} className={useMic ? 'MIC active' : 'MIC'} >
            <FiMic></FiMic>
          </div>
          <InputField
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={useMic ? "Hãy hỏi bất cứ câu hỏi nào về xe ..." : "Nhập tin nhắn của bạn..."}
            disabled={isLoading || useMic}
          />
          {!useMic && <SendButton
            onClick={sendMessage}
            disabled={isLoading || !inputValue.trim()}
          >
            <FiSend size={20} />
          </SendButton>}
        </ChatInput>
      </ChatContainer>
      <audio
        style={{ visibility: "hidden", position: "absolute" }}
        id="player"
        controls
      ></audio>
    </AppContainer >
  );
}

export default App;
