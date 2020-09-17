## 03_resetter

Need to provide an interface that will
  a) drive P0_0 (RST) on targe Olimex board -> [GND] (approx 10 micro-seconds)
                (RST) then -> (Float) 
  -- board will RE-SET 
  -- P0_3 tied to [GND] && BLD_E [CLOSED] therefore, ISP boot-loader will be chosen

##Implementation 03_resetter
## [CMD module] --> [RESETTER]
