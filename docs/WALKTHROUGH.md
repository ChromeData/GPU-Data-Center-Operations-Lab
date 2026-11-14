# Walkthrough

**Four short chapters · a looping clip and the steps for each**

The clips are sped up. The steps are the real commands. Start the lab with `.\START-DCLAB.ps1`.
Every BMC login is `admin` / `admin`.

| Chapter | In one line |
|---|---|
| [1. Walk the hall](#1-walk-the-hall) | Find the rack and open the ticket list. |
| [2. A live ticket](#2-a-live-ticket) | A server keeps shutting off. Find out why and fix it. |
| [3. Bench work](#3-bench-work) | Take a server out and tighten its power bar. |
| [4. Work orders](#4-work-orders) | Click the right part, then pick the right fix. |

## 1. Walk the hall

**Find the rack and open the ticket list.**

![Walking from the main floor to rack R12, then opening the ticket board](walkthrough/01-walk-the-hall.webp)

1. Click the hall once.
2. Left and Right turn. Up walks forward.
3. Stop when the label says **In front of R12**.
4. Open **Tickets** (top right).
5. Click a ticket. **TEACH** is what to know. **DO** is the job.

## 2. A live ticket

**A server keeps shutting off. Find out why and fix it.**

Ticket DCOPS-104. A leak sensor reads wrong because the BMC firmware is old. Update it.

![Ticket 104: collecting logs, updating the BMC, watching the tray boot over serial, then grading](walkthrough/02-live-ticket.webp)

1. Open the ticket and press **Start in Window 1**.
2. Go to the work folder: `dcgo`
3. Save the logs first, before changing anything:

   ```
   ipmitool -I lanplus -H <BMC_IP> -U admin -P admin sdr elist | tee -a <TAG>-sdr.txt
   ipmitool -I lanplus -H <BMC_IP> -U admin -P admin sel -v list | tee -a <TAG>-sel.txt
   curl -sk -u admin:admin https://<BMC_IP>/redfish/v1/Systems/HGX_Baseboard_0/LogServices/EventLog/Entries | jq | tee -a <TAG>-HMCevents.txt
   ```

4. Find the leak sensor that is not between 1.70 and 1.75 volts.
5. Check the BMC version against the site standard:

   ```
   curl -sk -u admin:admin https://<BMC_IP>/redfish/v1/UpdateService/FirmwareInventory/BMC_Firmware | jq .Version
   dclab matrix
   ```

6. Update the BMC with the server off: `tech fwupdate CT07 bmc 26.01.10001500`
7. In Window 2, watch the boot: `ipmitool ... sol activate`
8. In Window 1, power on: `ipmitool ... chassis power on`. Leave the console with Enter, then `~.`
9. Check the sensors again: `ipmitool ... sdr elist | grep Lea`. All four read 1.72 volts.
10. Write what was wrong and what fixed it in `resolution.txt`.
11. Run `dclab grade`.

Stuck? Try `dclab nudge`, then `dclab walk`, then `dclab show`.

## 3. Bench work

**Take a server out and tighten its power bar.**

Ticket DCOPS-106. The server has no power because the busbar screws are loose. `tech` is your hands.

![Ticket 106: the tray comes out of the rack, the lid opens, and the busbar is re-torqued](walkthrough/03-bench-work.webp)

1. `dclab start 106`
2. `tech pull CT12` puts the server on the bench.
3. `tech open CT12` opens the lid.
4. `tech inspect CT12 busbar` shows the loose screws.
5. `tech loosen CT12 busbar` loosens all of them first.
6. Tighten to 20 in-lb, in this order: back, front, middle.

   ```
   tech torque CT12 busbar --section back --inlb 20
   tech torque CT12 busbar --section front --inlb 20
   tech torque CT12 busbar --section middle --inlb 20
   ```

7. `tech uv CT12` checks for a coolant leak.
8. `tech close CT12`, then `tech insert CT12` puts it back in the rack.

To finish the ticket, save the logs, power on and run `dclab grade`, as in chapter 2.

## 4. Work orders

**Click the right part, then pick the right fix.**

Open **Quiz**, then **Work orders**. Drag to turn the model. Scroll to zoom.

![Six work orders: identify the part on the model, then choose the operation](walkthrough/04-work-orders.webp)

| Problem | Click this | Then do this |
|---|---|---|
| No power, voltage errors | The busbar | Loosen every screw, then 20 in-lb: back, front, middle |
| No power, HMC | The HMC board and its cable | Reseat both |
| Leak alarm | The leak sensor | Check the BMC version, UV light, clean the sensor, zip tie |
| Server swap | Handles, rails, NVMe drives, M.2 | Move them to the new server, then send the swap form |
| NVLink switch offline | The switch | Reset the spare, swap it in, let it set itself up |
| Cable cartridge | The cartridge label, at the rear | Read the NVIDIA serial number |

There are 25 work orders, plus six quick drill modes.
