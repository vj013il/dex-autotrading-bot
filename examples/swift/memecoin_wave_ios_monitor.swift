import Foundation
import SolanaMVP

let monitor = MemeCoinWaveMonitor(dex: RaydiumClient())
monitor.onSignal { token, change in
    print("Meme coin wave detected for \(token): \(change * 100)%")
}
monitor.start()
RunLoop.main.run()
