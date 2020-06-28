// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';

// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

	const RECPP_TERM = "recpp ext term";
	
	// This line of code will only be executed once when your extension is activated
	console.log('recpp extension activated');

	//vscode.window.onDidOpenTerminal((terminal: vscode.Terminal) => {
		//vscode.window.showInformationMessage(`onDidOpenTerminal, name: ${terminal.name}`);
	//});

	let reccp_cb = function(dish: string) {
		// Retrieve config up-to-date each time the command is executed
		const config = vscode.workspace.getConfiguration('recpp');

		// Check if the terminal exists
		const terminals = <vscode.Terminal[]>(<any>vscode.window).terminals;

		let terminal = terminals.find((element) => element.name === RECPP_TERM);
		if (terminal === undefined) {
			terminal = vscode.window.createTerminal({
				name: "recpp ext term",
				cwd: config.recpp,
				hideFromUser: false
			} as any);
		}

		terminal.show(false);
		terminal.sendText(`${config.python} recpp.py -d ${dish} -a`);
	
		// TODO: If/When the API will provide a way to wait for process completion
		//       + hook terminal output (onDidWriteTerminalData), it would be interesting
		//       to filter and copy code to active document
		/// let activeEditor = vscode.window.activeTextEditor;
		// activeEditor.edit((selectedText) => {
		//	selectedText.replace(activeEditor.selection, "newText");
		//})
	};

	context.subscriptions.push(vscode.commands.registerCommand('recpp.function', reccp_cb.bind(null, "function")));
	context.subscriptions.push(vscode.commands.registerCommand('recpp.class', reccp_cb.bind(null, "class")));
}

// this method is called when your extension is deactivated
export function deactivate() {}
