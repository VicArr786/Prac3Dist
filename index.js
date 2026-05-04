const app = require('express')();
const http = require('http').Server(app);
const io = require('socket.io')(http);
const port = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/index.html');
});

io.on('connection', (socket) => {
  socket.data.username = 'Anon';

  // Let the new client know it is connected and some basic info
  socket.emit('system message', {
    type: 'connected',
    text: 'Conectado al servidor',
    clients: io.engine.clientsCount,
  });

  // Broadcast current online count
  io.emit('system message', {
    type: 'presence',
    text: `Usuarios conectados: ${io.engine.clientsCount}`,
    clients: io.engine.clientsCount,
  });

  socket.on('set username', (username) => {
    const clean =
      typeof username === 'string' ? username.trim().slice(0, 24) : '';
    if (clean) socket.data.username = clean;

    socket.emit('system message', {
      type: 'identity',
      text: `Tu nombre es: ${socket.data.username}`,
      username: socket.data.username,
    });

    socket.broadcast.emit('system message', {
      type: 'join',
      text: `${socket.data.username} se ha unido`,
      username: socket.data.username,
      clients: io.engine.clientsCount,
    });
  });

  socket.on('chat message', msg => {
    const text = typeof msg === 'string' ? msg.trim() : '';
    if (!text) return;

    io.emit('chat message', {
      text,
      username: socket.data.username || 'Anon',
      ts: Date.now(),
    });
  });

  socket.on('disconnect', () => {
    io.emit('system message', {
      type: 'leave',
      text: `${socket.data.username || 'Anon'} se ha desconectado`,
      username: socket.data.username || 'Anon',
      clients: io.engine.clientsCount,
    });

    io.emit('system message', {
      type: 'presence',
      text: `Usuarios conectados: ${io.engine.clientsCount}`,
      clients: io.engine.clientsCount,
    });
  });
});

http.listen(port, () => {
  console.log(`Socket.IO server running at http://localhost:${port}/`);
});
