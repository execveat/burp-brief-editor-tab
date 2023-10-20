from burp import IBurpExtender, IMessageEditorTabFactory, IMessageEditorTab
from javax.swing import JPanel, JSplitPane, JLabel, BorderFactory
from java.awt import BorderLayout, Font

class BurpExtender(IBurpExtender, IMessageEditorTabFactory):
    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        callbacks.setExtensionName("Brief Editor View")
        callbacks.registerMessageEditorTabFactory(self)

    def createNewInstance(self, controller, editable):
        return BriefEditorTab(self.callbacks, controller, editable)

class BriefEditorTab(IMessageEditorTab):
    def __init__(self, callbacks, controller, editable):
        self._editable = editable
        self._txtHeaders = callbacks.createTextEditor()
        self._txtInput = callbacks.createMessageEditor(None, editable)
        self._txtHeaders.setEditable(editable)
        self.setup_ui()

    def setup_ui(self):
        """Setting up the user interface components."""
        # Set up the bottom panel with "Headers" label
        bottom_panel = JPanel(BorderLayout())
        bottom_panel.add(self._txtHeaders.getComponent(), BorderLayout.CENTER)

        headersLabel = JLabel("Headers")
        headersLabel.setBorder(BorderFactory.createEmptyBorder(5, 5, 5, 5))
        headersLabel.setFont(headersLabel.getFont().deriveFont(14.0).deriveFont(Font.BOLD))
        bottom_panel.add(headersLabel, BorderLayout.NORTH)

        # Set up the split pane with the text input and headers
        self._panel = JPanel(BorderLayout())
        self._splitPane = JSplitPane(JSplitPane.VERTICAL_SPLIT)
        self._splitPane.setTopComponent(self._txtInput.getComponent())
        self._splitPane.setBottomComponent(bottom_panel)
        self._splitPane.setResizeWeight(0.75)

        self._panel.add(self._splitPane, BorderLayout.CENTER)

    def getUiComponent(self):
        return self._panel

    def getMessage(self):
        """Combining headers and body parts of the message."""
        headers = self._txtHeaders.getText()
        main_parts = self._txtInput.getMessage().split("\r\n")
        first_line = main_parts[0]
        body = "\r\n".join(main_parts[2:])

        return first_line + "\r\n" + headers + "\r\n\r\n" + body

    def setMessage(self, content, isRequest):
        """Setting the message content in the editor."""
        if content:
            headers, main = self.splitMessage(content.tostring())
            self._txtHeaders.setText(headers)
            self._txtInput.setMessage(main, isRequest)

    def splitMessage(self, message):
        """Splitting the message into headers and main parts."""
        try:
            lines = message.split("\r\n")
            first_empty_line = lines.index("")

            headers = "\r\n".join(lines[1:first_empty_line])
            main = lines[0] + "\r\n\r\n" + "\r\n".join(lines[first_empty_line + 1:])

            return headers, main
        except:
            return None, message

    def getTabCaption(self):
        return "Brief"

    def isEnabled(self, content, isRequest):
        return True

    def isModified(self):
        return self._txtInput.isMessageModified() or self._txtHeaders.isTextModified()
