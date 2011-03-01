import java.io.IOException;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;

public class client {    
    // Build parameter string for gMiner
    public static final String content = "[gMiner]" + "\n" + "version=0.1.5"
                                         
    + "\n" + "track1=/scratch/tracks/qual/sql/ribosome_genesis.sql"
    + "\n" + "track1_name='Fake client track one'"
    + "\n" + "track2=/scratch/tracks/qual/sql/ribosome_proteins.sql"
    + "\n" + "track2_name='Fake client track two'"
    + "\n" + "operation_type=desc_stat"
    + "\n" + "characteristic=number_of_features"
    + "\n" + "per_chromosome=True"
    + "\n" + "compare_parents=False"
                                                                    + "";
                                         
    // The url for posting
    public static final String address = "http://www.example.com/gMiner/";
    
    public void sendPostRequest() {
        // Declare variables
        URL                 url    = null;
        HttpURLConnection   conn   = null;
        DataOutputStream    output = null;
        DataInputStream     input  = null;
        DataInputStream     error  = null;
        String              buffer = null;
        try {            
            // URL of web service
            url = new URL(address);
            // HTTP connection channel.
            conn = (HttpURLConnection) url.openConnection();
            // Let the run-time system (RTS) know that we want input.
            conn.setDoInput(true);
            // Let the RTS know that we want to do output.
            conn.setDoOutput(true);
            // Specify the method
            conn.setRequestMethod("POST");
            // No caching, we want the real thing.
            conn.setUseCaches(false);
            // Specify the content type and size.
            conn.setRequestProperty("Content-Type", "text/plain");
            conn.setRequestProperty("Content-Length", "" + content.length());
            // Create output stream
            output = new DataOutputStream(conn.getOutputStream());
            // Send POST output.
            output.writeBytes(content);
            output.flush();
            output.close();
            // Create input stream
            input = new DataInputStream(conn.getInputStream());
            // Print all lines
            while (null != ((buffer = input.readLine()))){System.out.println(buffer);}
            // Close the stream
            input.close ();
        } catch (MalformedURLException ex) {
            ex.printStackTrace();
        } catch (IOException ex) {
            error = new DataInputStream(conn.getErrorStream());
            try {
                while (null != ((buffer = error.readLine()))){System.out.println(buffer);}
            } catch (IOException e) {
                e.printStackTrace();
            }
            ex.printStackTrace();
        } finally { 
            
        }
    }

    public static void main(String[] args) {
        new client().sendPostRequest();
    }
}
