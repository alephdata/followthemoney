package tech.followthemoney.meta;

import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.util.Random;

public class Version {
    private static final DateTimeFormatter FORMATTER = DateTimeFormatter.ofPattern("yyyyMMddHHmmss").withZone(ZoneId.from(ZoneOffset.UTC));
    private static final String ENCODING = "0123456789abcdefghijklmnopqrstuvwxyz";

    private static String encodeTag(int num) {
        StringBuilder result = new StringBuilder();
        while (num > 0) {
            result.insert(0, ENCODING.charAt(num % ENCODING.length()));
            num /= ENCODING.length();
        }
        return result.toString();
    }

    public static String create(String tag) {
        Instant now = Instant.now().truncatedTo(ChronoUnit.SECONDS);
        
        if (tag == null) {
            long microPart = System.nanoTime() / 1000 / 1000 % 1000;
            int tagNum = (int)(microPart / 100) * 10;
            tagNum += new Random().nextInt(10);
            tag = encodeTag(tagNum);
        }

        tag = String.format("%-3s", tag).substring(0, 3).replace(' ', 'x');
        return String.format("%s-%s", FORMATTER.format(now), tag);
    }

    public static String create() {
        return create(null);
    }
}
