<!doctype html>
<head>
    <meta charset="utf-8" />
    <title>WebSocket</title>

    <style>
        li { list-style: none; }
    </style>

    <script src="/static/js/jquery.min.js"></script>
    <script>
        $(document).ready(function() {
            if (!window.WebSocket) {
                if (window.MozWebSocket) {
                    window.WebSocket = window.MozWebSocket;
                } else {
                    $('#messages').append("<li>Your browser doesn't support WebSockets.</li>");
                }
            }
            ws = new WebSocket('ws://127.0.0.1:6001/api/v1/game/ws/check');
            ws.onopen = function(evt) {
                // $('#messages').append('<li>connected.</li>');
            }
            ws.onmessage = function(evt) {
                $('#messages').append('<li>' + evt.data + '</li>');
            }
            $('#send-message').submit(function() {
                ws.send($('#name').val() + ": " + $('#message').val());
                $('#message').val('').focus();
                return false;
            });
        });
    </script>
</head>
<body>
    <!--
    <form id="send-message">
        <input id="name" type="text" value="name">
        <input id="message" type="text" value="message" />
        <input type="submit" value="Send" />
    </form>
    -->
    <div id="messages"></div>
</body>
</html>