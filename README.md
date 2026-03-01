# SDA-PHASE-2  

Let me first try to give a little intro to typing protocols, or atleast the way I understood it (It's prolly wrong, but if it helps, it helps :) ).
A protocol is an abstract class that allows you to implement polymorphism in python without the child classes having to inherit from the abstract class, like we had to do in C++. Instead, we define certain functions in the protocol class. And then any other random class in our project that contains functions from the abstract class, are treated like they're like that abstract class.  

To give an example, the protocols in our project are defined in core/contracts.py. We only have 2 protocols: PipleLineService(for the reader), and DataSink(for the writer). Now consider the DataSink class. It has only a single function called write(). Now, we defined the CONSOLEWRITER in plugins/output.py. The Consolewriter has a write() function, and is thus treated like a DataSink in our main.py.  

# MAIN.PY  
This is the entrypoint to the code. It loads config. Selects Reader. Selects Writer. It passes Writer to the TransformationEnging in engine.py, which is then passed on to Reader. 



# DATA
This contains the global gdp data files, easy enough.  


# CORE
Now this has two module: contracts.py and engine.py
I've already explained contracts.py. engine.py is the processor of our code. If you are going to perform calculations, filter data, or whatever, you need to perform them in the execute() function of engine.py

# PLUGINS  
plugins are where we define our csvReader, JsonReader, ConsoleWriter, and graphWriter. 
