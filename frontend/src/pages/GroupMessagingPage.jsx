import { useCallback, useEffect, useMemo, useState } from "react";
import { messagesAPI } from "../services/api";

function GroupMessagingPage() {
  const [conversations, setConversations] = useState([]);
  const [selectedConversationId, setSelectedConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [newConversationName, setNewConversationName] = useState("");
  const [participantEmails, setParticipantEmails] = useState("");
  const [directory, setDirectory] = useState([]);
  const [userSearch, setUserSearch] = useState("");
  const [selectedParticipantIds, setSelectedParticipantIds] = useState([]);
  const [error, setError] = useState("");
  const [directoryError, setDirectoryError] = useState("");
  const [loading, setLoading] = useState(true);

  const currentUser = useMemo(() => {
    try {
      return JSON.parse(localStorage.getItem("user") || "{}");
    } catch {
      return {};
    }
  }, []);

  const loadConversations = useCallback(async () => {
    try {
      const res = await messagesAPI.listConversations();
      const list = res.data || [];
      setConversations(list);
      if (!selectedConversationId && list.length) {
        setSelectedConversationId(list[0].id);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load conversations");
    }
  }, [selectedConversationId]);

  const loadDirectory = async (query = "") => {
    try {
      setDirectoryError("");
      const res = await messagesAPI.listUsers ? messagesAPI.listUsers(query, 30) : null;
      if (res) setDirectory(res.data || []);
    } catch (err) {
      setDirectoryError(err.response?.data?.detail || "Failed to load user directory for messaging");
      setDirectory([]);
    }
  };

  const loadMessages = async (conversationId) => {
    if (!conversationId) return;
    try {
      const res = await messagesAPI.getConversationMessages(conversationId);
      setMessages(res.data?.messages || []);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load messages");
    }
  };

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      await loadConversations();
      await loadDirectory();
      setLoading(false);
    };
    init();
  }, [loadConversations]);

  useEffect(() => {
    const timer = setTimeout(() => loadDirectory(userSearch), 300);
    return () => clearTimeout(timer);
  }, [userSearch]);

  useEffect(() => {
    loadMessages(selectedConversationId);
  }, [selectedConversationId]);

  useEffect(() => {
    if (!selectedConversationId) return undefined;
    const timer = setInterval(() => {
      loadMessages(selectedConversationId);
      loadConversations();
    }, 3000);
    return () => clearInterval(timer);
  }, [selectedConversationId, loadConversations]);

  const handleCreateConversation = async () => {
    setError("");
    try {
      const participantIds = selectedParticipantIds;
      let resolvedIds = participantIds;
      if (!resolvedIds.length && participantEmails.trim()) {
        const emails = participantEmails
          .split(",")
          .map((e) => e.trim())
          .filter(Boolean);
        const resolveRes = await messagesAPI.resolveParticipants(emails);
        const found = resolveRes.data?.found || [];
        const missing = resolveRes.data?.missing || [];
        if (missing.length) {
          throw new Error(`These users were not found: ${missing.join(", ")}`);
        }
        resolvedIds = found.map((u) => u.id);
      }
      if (!resolvedIds.length) {
        throw new Error("Select participants or enter participant emails");
      }
      const payload = {
        type: newConversationName.trim() ? "group" : "one_to_one",
        name:
          newConversationName.trim() ||
          (resolvedIds.length === 1
            ? (participantEmails.split(",").map((e) => e.trim()).filter(Boolean)[0] || null)
            : null),
        participant_ids: resolvedIds,
      };
      await messagesAPI.createConversation(payload);
      setNewConversationName("");
      setSelectedParticipantIds([]);
      setParticipantEmails("");
      await loadConversations();
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Failed to create conversation");
    }
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !selectedConversationId) return;
    setError("");
    try {
      await messagesAPI.sendMessage(selectedConversationId, {
        conversation_id: selectedConversationId,
        content: newMessage.trim(),
      });
      setNewMessage("");
      await loadMessages(selectedConversationId);
      await loadConversations();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to send message");
    }
  };

  if (loading) return <div className="p-4">Loading conversations...</div>;

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Secure Messaging (Live Polling)</h2>
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      {directoryError ? <p className="text-sm text-red-600">{directoryError}</p> : null}

      <div className="rounded border p-4">
        <p className="mb-2 text-sm font-medium">Create conversation</p>
        <input
          className="mb-2 w-full rounded border px-3 py-2"
          placeholder="Group name (optional)"
          value={newConversationName}
          onChange={(e) => setNewConversationName(e.target.value)}
        />
        <input
          className="mb-2 w-full rounded border px-3 py-2"
          placeholder="Search users by email or name"
          value={userSearch}
          onChange={(e) => setUserSearch(e.target.value)}
        />
        <input
          className="mb-2 w-full rounded border px-3 py-2"
          placeholder="Or enter participant emails (comma-separated)"
          value={participantEmails}
          onChange={(e) => setParticipantEmails(e.target.value)}
        />
        <div className="max-h-32 overflow-y-auto rounded border p-2">
          {directory.map((u) => (
            <label key={u.id} className="mb-1 flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={selectedParticipantIds.includes(u.id)}
                onChange={(e) => {
                  if (e.target.checked) {
                    setSelectedParticipantIds((prev) => [...prev, u.id]);
                  } else {
                    setSelectedParticipantIds((prev) => prev.filter((id) => id !== u.id));
                  }
                }}
              />
              <span>
                {u.first_name} {u.last_name} ({u.email})
              </span>
            </label>
          ))}
          {directory.length === 0 ? (
            <p className="text-xs text-slate-500">
              No users found. Ensure the other user is registered in backend, then search by name/email.
            </p>
          ) : null}
        </div>
        <button className="mt-2 rounded bg-indigo-600 px-3 py-1 text-white" onClick={handleCreateConversation}>
          Create
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="rounded border">
          <div className="border-b p-3 font-medium">Conversations</div>
          <div className="max-h-[500px] overflow-y-auto p-2">
            {conversations.map((conv) => (
              <button
                key={conv.id}
                onClick={() => setSelectedConversationId(conv.id)}
                className={`mb-2 w-full rounded border px-3 py-2 text-left ${
                  selectedConversationId === conv.id ? "border-indigo-500 bg-indigo-50" : ""
                }`}
              >
                <div className="font-medium">{conv.name || `Conversation #${conv.id}`}</div>
                <div className="text-xs text-slate-500">{conv.type}</div>
              </button>
            ))}
            {conversations.length === 0 ? <p className="text-sm text-slate-500">No conversations yet.</p> : null}
          </div>
        </div>

        <div className="rounded border lg:col-span-2">
          <div className="border-b p-3 font-medium">Messages</div>
          <div className="max-h-[420px] overflow-y-auto p-3">
            {messages.map((msg) => {
              const mine = msg.sender_id === currentUser.id;
              return (
                <div key={msg.id} className={`mb-3 flex ${mine ? "justify-end" : "justify-start"}`}>
                  <div className={`max-w-[80%] rounded px-3 py-2 ${mine ? "bg-indigo-600 text-white" : "bg-slate-100"}`}>
                    <p className="text-sm break-words">{msg.content_encrypted}</p>
                    <p className={`mt-1 text-xs ${mine ? "text-indigo-200" : "text-slate-500"}`}>
                      {new Date(msg.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              );
            })}
            {messages.length === 0 ? <p className="text-sm text-slate-500">No messages in this conversation.</p> : null}
          </div>
          <div className="border-t p-3">
            <div className="flex gap-2">
              <input
                className="flex-1 rounded border px-3 py-2"
                value={newMessage}
                placeholder="Type message"
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleSendMessage();
                }}
              />
              <button className="rounded bg-indigo-600 px-4 py-2 text-white" onClick={handleSendMessage}>
                Send
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default GroupMessagingPage;
