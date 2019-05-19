//Release History
//		1.0 May 20, 2016
//			Initial Release

// Ported to Hubitat 5/14/2019 - AJax
// Borrowed from Cobra

metadata {
	definition (name: "Virtual Phone Presence Plus", namespace: "AJax", author: "Adam Gardner") {
        attribute "BluetoothMacAddress", "string";
		capability "Switch";
 //       capability "Refresh"
        capability "Presence Sensor";
		capability "Sensor";
        
		command "arrived";
		command "departed";

		preferences() {
			section("Query Inputs"){
				input "BluetoothMacAddress", "text", required: true, title: "Device BT Mac Addr";
			}
		}
    }
}

def installed() {
    initialize();
}

def updated() {
    initialize();
}

def initialize() {
	sendEvent(name: "BluetoothMacAddress", value: BluetoothMacAddress)
}

def parse(String description) {
	def pair = description.split(":")
	createEvent(name: pair[0].trim(), value: pair[1].trim())
}

// handle commands
def arrived() {
	on()
}


def departed() {
    off()
}

def on() {
	sendEvent(name: "switch", value: "on")
    sendEvent(name: "presence", value: "present")

}

def off() {
	sendEvent(name: "switch", value: "off")
    sendEvent(name: "presence", value: "not present")

}