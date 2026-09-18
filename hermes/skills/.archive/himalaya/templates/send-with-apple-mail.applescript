set recipientEmail to "recipient@example.com"
set recipientName to "Recipient Name"
set emailSubject to "Subject line"
set attachmentPath to POSIX file "/absolute/path/to/attachment.pdf"
set emailBody to "Hi Recipient,

Write the plain-text email body here.

Best,
Sender"

tell application "Mail"
    set newMessage to make new outgoing message with properties {subject:emailSubject, content:emailBody & return & return, visible:false}
    tell newMessage
        make new to recipient at end of to recipients with properties {name:recipientName, address:recipientEmail}
        make new attachment with properties {file name:attachmentPath} at after the last paragraph
        send
    end tell
end tell
